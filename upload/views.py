from django.shortcuts import render, redirect
from upload.forms import SubmissionForm
from upload.models import Submission
import upload.models
from upload.models import Student, Course
import os.path
import time
from SubGit.settings import MEDIA_ROOT
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from github import Github
from decouple import config
from git import Repo
from git import Git
import sys
from upload.submit import submit


def handle_uploaded_file(f, file_path):
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


@login_required
def model_form_upload(request, course_id):
    username = request.user.username
    course_directory = os.path.join(MEDIA_ROOT, username, course_id)
    # if a file is being uploaded
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            filename = str(request.FILES['file']).replace(" ", "_")
            file_path = os.path.join(course_directory, filename)

            handle_uploaded_file(request.FILES['file'], file_path)

            # wait until the upload has finished, then submit to Git
            while not os.path.exists(file_path):
                time.sleep(1)

            if os.path.isfile(file_path):
                submit(username, course_id, filename)
            else:
                return redirect('/error/')

            return redirect('/submitted/{}'.format(course_id))

    # if no file is being uploaded, display an empty form
    else:
        form = SubmissionForm()

    repo_directory = os.path.join(course_directory, ".git")
    if os.path.exists(repo_directory):
        repo_name = "{}-{}".format(course_id, username)
        return render(request, 'upload/model_form_upload.html', {
            'form': form,
            'course': course_id,
            'url': "https://github.com/{}/{}" \
                      .format(config("GITHUB_ADMIN_USERNAME"), repo_name)
        })
    else:
        return redirect('/register/')


def not_registered(request):
    return render(request, 'upload/not_registered.html')


def error(request):
    return render(request, 'upload/error.html')


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')


@login_required
def submitted(request, course_id):
    # test of displaying submission history
    # documents = Submission.objects.all()
    # return render(request, 'submitted.html', {'documents': documents})
    repo_name = "{}-{}".format(course_id, request.user.username)
    return render(request, 'upload/submitted.html', {
        'course': course_id,
        'url': "https://github.com/{}/{}".format(
            config("GITHUB_ADMIN_USERNAME"), repo_name)
    })


@login_required
def courses(request):
    user_directory = os.path.join(MEDIA_ROOT, request.user.username)
    if os.path.exists(user_directory):
        return render(request, 'upload/courses.html', {
            'courses': Student.objects.get(username=request.user.username).courses.all()
        })
    else:
        return redirect('/register/')


@login_required
def connect_github(request, course_id):
    repo_name = "{}-{}".format(course_id, request.user.username)
    if request.method == 'POST':
        gitUsername = request.POST.get('username')
        g = Github(config("GITHUB_ADMIN_USERNAME"),
                   config("GITHUB_ADMIN_PASSWORD"))
        repo = g.get_user().get_repo(repo_name)
        repo.add_to_collaborators(gitUsername, "push")
        return redirect("/courses/")

    repo_url = "git@github.com:{}/{}.git".format(
        config("GITHUB_ADMIN_USERNAME"), repo_name)
    return render(request, "upload/connect_github.html", {
        'url': repo_url,
        'course_id': course_id
    })


@login_required
def register(request):
    if request.method == 'POST':
        username = request.user.username

        courseId = request.POST.get('course-id')
        course, new = Course.objects.get_or_create(id=courseId)
        if new:
            course.save()

        student, new = Student.objects.get_or_create(username=username)
        if not student.courses.filter(id=courseId).exists():
            student.courses.add(course)
            student.save()

        user_directory = os.path.join(MEDIA_ROOT, username, courseId)
        os.makedirs(user_directory)

        # TODO: break up this try block
        try:
            g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))
            repo_name = "{}-{}".format(courseId, username)
            g.get_user().create_repo(repo_name)

            #repo_url = "https://github.com/{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)
            repo_url = "git@github.com:{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)

            # TODO: move to environment variable
            git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
            git_ssh_cmd = "ssh -i {}".format(git_ssh_identity_file)

            with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                local_repo = Repo.clone_from(repo_url, user_directory)

            readme_path = make_readme(username, user_directory)

            local_repo.index.add([readme_path])
            local_repo.index.commit("Initial commit")
            origin = local_repo.remotes.origin
            origin.push()

            return redirect('/courses/')
        except Exception as e:
            print(e)
            print("Unexpected error:", sys.exc_info()[0])
            return redirect('/error/')

    return render(request, 'upload/register.html', {
        'courses': Course.objects.all()
    })


def make_readme(username, user_directory):
    readme_path = os.path.join(user_directory, "README.md")
    with open(readme_path, "w+") as readme:
        readme.write("Homework submission repository for {}".format(
            username))
        readme.close()
    return readme_path


@login_required
def registered(request):
    return render(request, 'upload/registered.html')


def home(request):
    if request.user.username:
        return redirect("/courses/")
    return render(request, 'upload/home.html')
