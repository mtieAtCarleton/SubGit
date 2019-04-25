# from https://stackoverflow.com/questions/38594717/how-do-i-push-new-files-to-github
from git import Repo
from SubGit.settings import MEDIA_ROOT
from decouple import config
import os, git


def submit(user, course_id, file_names, commit_message, branch):
    repo_dir = os.path.join(MEDIA_ROOT, user, course_id)
    repo = Repo(repo_dir)

    file_list = [
        os.path.join(MEDIA_ROOT, user, course_id, fileName) for fileName in file_names
    ]

    try:
        repo.git.checkout(branch)
    except git.exc.GitCommandError as e:
        repo.git.checkout('-b', branch)

    repo.index.add(file_list)
    repo.index.commit(commit_message)
    repo.git.push('--set-upstream', 'origin', branch)
    # origin = repo.remote('origin')
    # origin.pull()
    # origin.push()
