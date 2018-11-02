from django.shortcuts import render, redirect
from upload.forms import SubmissionForm
from upload.models import Submission
import upload.models
import os.path
import time
from SubGit.settings import MEDIA_ROOT
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from github import Github
from decouple import config
from git import Repo
import sys
from upload.submit import submit


def model_form_upload(request):
    # if a file is being uploaded
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # update the model so it knows whose directory to upload to - this is janky and should be fixed
            upload.models.gitUsername = request.user

            # upload the file
            form.save()
            filename = str(request.FILES['document']).replace(" ", "_")
            filePath = '{}/{}/{}'.format(MEDIA_ROOT, request.user, filename)

            # wait until the upload has finished, then submit to Git
            while not os.path.exists(filePath):
                time.sleep(1)

            if os.path.isfile(filePath):
                submit(request.user, filename)
                print("submit")
            else:
                print("file not found")
                return redirect('/error/')

            return redirect('/submitted/')

    # if no file is being uploaded, display an empty form
    else:
        form = SubmissionForm()

    # test if user already has a directory in the class repo
    user_directory = '{}/{}/'.format(MEDIA_ROOT, request.user)
    if os.path.exists(user_directory):
        return render(request, 'upload/model_form_upload.html', {
            'form': form
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
    return render(request, 'upload/submitted.html')


def register(request):
    if request.method == 'POST':
        gitUsername = request.POST.get('username')
        user_directory = '{}/{}/'.format(MEDIA_ROOT, request.user)
        try:
            g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))
            admin = g.get_user()

            repo_name = "csXXX-{}".format(request.user)
            repo = admin.create_repo(repo_name)
            #repo.add_to_collaborators(gitUsername, "push")

            os.mkdir(user_directory)
            #repo_directory = "{}/{}/".format(user_directory, repo_name)
            #os.mkdir(repo_directory)

            repo_url = "https://github.com/{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)
            local_repo = Repo.init(user_directory)

            readme_path = "{}/{}".format(user_directory, "README.md")
            print(readme_path)
            with open(readme_path, "w+") as readme:
                readme.write("Homework submission repository for " + str(request.user))
                readme.close()

            print("adding", readme_path)
            local_repo.index.add([readme_path])
            print("committing")
            local_repo.index.commit("Initial commit")


            origin = local_repo.create_remote('origin', repo_url)
            local_repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master)
            origin.push()
            return redirect('/upload/')
        except Exception as e:
            print(e)
            print("Unexpected error:", sys.exc_info()[0])
            return redirect('/error/')

    return render(request, 'upload/register.html')


def registered(request):
    print(request.user)
    return render(request, 'upload/registered.html')


def home(request):
    return render(request, 'upload/home.html')
