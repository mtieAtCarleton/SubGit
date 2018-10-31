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
                #submit(request.user, filename)
                print("submit")
            else:
                raise ValueError("File error: {} not found".format(filename))

            return redirect('/submitted/')

    # if no file is being uploaded, display an empty form
    else:
        form = SubmissionForm()

    # test if user already has a directory in the class repo
    print(request.user)
    if (request.user.email):
        upload.models.username = str(request.user)
        print(request.user.email)
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
        print(gitUsername, request.user)
        user_directory = '{}/{}/'.format(MEDIA_ROOT, request.user)
        try:
            os.mkdir(user_directory)
        except:
            return redirect('/error/')


    return render(request, 'upload/register.html')

def registered(request):
    print(request.user)
    return render(request, 'upload/registered.html')

def home(request):
    return render(request, 'upload/home.html')
