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


def model_form_upload(request):
    # if a file is being uploaded
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            courseId = Student.objects.get(
                username=request.user.username).courses.all().first().id
            directory = os.path.join(MEDIA_ROOT, request.user.username,
                                    courseId)

            # update the model so it knows whose directory to upload to - this is janky and should be fixed
            # TODO: fix this
            upload.models.dir = directory

            # upload the file
            form.save()
            filename = str(request.FILES['document']).replace(" ", "_")
            #filePath = '{}/{}/{}'.format(MEDIA_ROOT, request.user, filename)
            filePath = os.path.join(directory, filename)
            # wait until the upload has finished, then submit to Git
            while not os.path.exists(filePath):
                time.sleep(1)

            if os.path.isfile(filePath):
                submit(request.user.username, courseId, filename)
                print("submit")
            else:
                print("file not found")
                return redirect('/error/')

            return redirect('/submitted/')

    # if no file is being uploaded, display an empty form
    else:
        form = SubmissionForm()

    # test if user already has a directory in the class repo
    #user_directory = '{}/{}/.git'.format(MEDIA_ROOT, request.user)
    #TODO: revert this to checking for a class-specific repo
    user_directory = os.path.join(MEDIA_ROOT, request.user.username)
    if os.path.exists(user_directory):
        courseId = Student.objects.get(
            username=request.user.username).courses.all().first().id
        repo_name = "{}-{}".format(courseId, request.user.username)
        return render(request, 'upload/model_form_upload.html', {
            'form': form,
            'course': courseId,
            'url': "https://github.com/{}/{}".format(config("GITHUB_ADMIN_USERNAME"), repo_name)
        })
    else:
        return redirect('/register/')


# Create your views here.
def not_registered(request):
    return render(request, 'upload/not_registered.html')


def error(request):
    return render(request, 'upload/error.html')


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')


def submitted(request):
    # test of displaying submission history
    # documents = Submission.objects.all()
    # return render(request, 'submitted.html', {'documents': documents})
    courseId = Student.objects.get(
        username=request.user.username).courses.all().first().id
    repo_name = "{}-{}".format(courseId, request.user.username)
    return render(request, 'upload/submitted.html', {
        'course': courseId,
        'url': "https://github.com/{}/{}".format(
            config("GITHUB_ADMIN_USERNAME"), repo_name)
    })


def courses(request):
    #TODO: revisit this
    user_directory = os.path.join(MEDIA_ROOT, request.user.username)
    if os.path.exists(user_directory):
        return render(request, 'upload/courses.html', {
            'courses': Student.objects.get(username=request.user.username).courses.all()
        })
    else:
        return redirect('/register/')


def connect_github(request):
    if request.method == 'POST':
        gitUsername = request.POST.get('username')
        # repo.add_to_collaborators(gitUsername, "push")


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

        #TODO: break up this try block
        try:
            g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))
            admin = g.get_user()

            repo_name = "{}-{}".format(courseId, username)
            repo = admin.create_repo(repo_name)

            #repo_url = "https://github.com/{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)
            repo_url = "git@github.com:{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)

            #TODO: move to environment variable
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


def registered(request):
    return render(request, 'upload/registered.html')


def home(request):
    if request.user.username:
        return redirect("/courses/")
    return render(request, 'upload/home.html')
