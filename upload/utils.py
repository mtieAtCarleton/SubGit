"""
Miscellaneous functions for use in views.py and elsewhere.
"""
from SubGit.settings import MEDIA_ROOT
from upload.models import File, Submission, Person, Course, GitHubAccount, Assignment

import os
import sys
import time

from decouple import config
import git
from git import Git
from git import Repo
from github import Github


def clone_course_repo(course_id, repo_name, username):
    g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))
    g.get_user().get_repo(repo_name)
    repo_url = "git@github.com:{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)
    user_directory = os.path.join(MEDIA_ROOT, username, course_id)
    # TODO: move to environment variable
    git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
    git_ssh_cmd = "ssh -i {}".format(git_ssh_identity_file)
    with git.Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        Repo.clone_from(repo_url, user_directory)


def submit(user, course_id, file_names, commit_message, branch):
    # from https://stackoverflow.com/questions/38594717/how-do-i-push-new-files-to-github
    repo_dir = os.path.join(MEDIA_ROOT, user, course_id)
    repo = Repo(repo_dir)

    master = repo.heads.master
    repo.git.pull('origin', master)

    file_list = [os.path.join(MEDIA_ROOT, user, course_id, fileName) for fileName in file_names]

    try:
        repo.git.checkout(branch)
    except git.exc.GitCommandError as e:
        print(e)
        repo.git.checkout('-b', branch)

    repo.index.add(file_list)
    repo.index.commit(commit_message)
    repo.git.push('--set-upstream', 'origin', branch)


def add_student_to_course(username, course_id):
    user_directory = os.path.join(MEDIA_ROOT, username, course_id)
    os.makedirs(user_directory)

    g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))
    repo_name = "{}-{}".format(course_id, username)

    # TODO: create within organization?
    try:
        repo = g.get_user().create_repo(repo_name, private=True)
    except GithubException as e:
        print(e)

    # TODO: break up this try block, improve error handling
    try:
        github_accounts = Person.objects.get(username=username).github_accounts.all()
        for account in github_accounts:
            repo.add_to_collaborators(account.username, "push")

        repo_url = "git@github.com:{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)

        # TODO: move to environment variable
        # see https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
        git_ssh_identity_file = os.path.expanduser(config('SSH_KEY_PATH'))
        git_ssh_cmd = "ssh -i {}".format(git_ssh_identity_file)
        time.sleep(2)
        with Git(user_directory).custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
            local_repo = Repo.clone_from(repo_url, user_directory)

        readme_path = make_readme(username, user_directory)
        # TODO: override any existing git config of username/password and use SubGitAdmin instead
        local_repo.index.add([readme_path])
        local_repo.index.commit("Initial commit")
        origin = local_repo.remotes.origin
        origin.push()

    except Exception as e:
        print(e)
        print("Unexpected error:", sys.exc_info()[0])


def get_branch_url(repo_name, assignment_title):
    return "https://github.com/{}/{}/tree/{}".format(config("GITHUB_ADMIN_USERNAME"), repo_name,
                                                     assignment_title.replace(" ", "_"))


def get_github_url(repo_name):
    return "https://github.com/{}/{}".format(config("GITHUB_ADMIN_USERNAME"), repo_name)


def clear_file(assignment_id, file, username):
    other_assignment_check = File.objects.filter(file=file.file, person__username=username).exclude(
        assignment__id=assignment_id)
    file_path = os.path.join(MEDIA_ROOT, file.file.name)
    if os.path.exists(file_path) and not other_assignment_check:
        os.remove(file_path)
    file.delete()


def get_submission_items(username, course_id, assignment_id):
    if assignment_id:
        files = File.objects.filter(submission__isnull=False, person__username=username, assignment__id=assignment_id)
    else:
        files = File.objects.filter(submission__isnull=False, person__username=username,
                                    assignment__course__id=course_id)
    submissions = {}
    repo_name = "{}-{}".format(course_id, username)
    github_url = "https://github.com/{}/{}".format(config("GITHUB_ADMIN_USERNAME"), repo_name)
    for file in files:
        filename = file.file.name.split('/')[-1]
        corresponding_assignment = file.assignment.title.replace(" ", "_")
        url = "{}/blob/{}/{}".format(github_url, corresponding_assignment, filename)
        if file.submission in submissions:
            submissions[file.submission].append((file, url, filename))
        else:
            submissions[file.submission] = [(file, url, filename)]
    submissions_items = sorted(submissions.items(), key=lambda submission: submission[0].submitted_at, reverse=True)
    return submissions_items


def make_readme(username, user_directory):
    readme_path = os.path.join(user_directory, "README.md")
    with open(readme_path, "w+") as readme:
        readme.write("Homework submission repository for {}".format(
            username))
        readme.close()
    return readme_path
