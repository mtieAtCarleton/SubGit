from django.shortcuts import render, redirect
from upload.forms import SubmissionForm
from SubGit.submit import submit
import upload.models
import os.path
import time
from SubGit.settings import MEDIA_ROOT
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

@login_required
def model_form_upload(request):
    # if a file is being uploaded
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # update the model so it knows whose directory to upload to - this is janky and should be fixed
            upload.models.gitUsername = request.user

            # upload the file
            form.save()
            filePath = '{}/uploads/{}/{}'.format(MEDIA_ROOT, request.user, request.FILES['document'])

            # wait until the upload has finished, then submit to Git
            while not os.path.exists(filePath):
                time.sleep(1)

            if os.path.isfile(filePath):
                submit(request.user, request.FILES['document'])
            else:
                raise ValueError("File error: {} not found".format(request.FILES['document']))

            return redirect('/')

    # if no file is being uploaded, display an empty form
    else:
        form = SubmissionForm()

    # test if user already has a directory in the class repo
    user_directory = '{}/uploads/{}/'.format(MEDIA_ROOT, request.user)
    if os.path.exists(user_directory):
        return render(request, 'model_form_upload.html', {
            'form': form
        })
    else:
        return redirect('/')

def home(request):
    return render(request, 'home.html')

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')