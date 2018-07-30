
# Create your views here.
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from upload.forms import SubmissionForm
from SubGit.submit import submit
from upload.models import Submission
import os.path
import time
from SubGit.settings import MEDIA_ROOT
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

@login_required
def model_form_upload(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            filePath = '{}/uploads/{}'.format(MEDIA_ROOT, request.FILES['document'])
            while not os.path.exists(filePath):
                time.sleep(1)

            if os.path.isfile(filePath):
                submit(request.user, request.FILES['document'])
            else:
                raise ValueError("File error: {} not found".format(request.FILES['document']))

            return redirect('/')
    else:
        form = SubmissionForm()
    return render(request, 'model_form_upload.html', {
        'form': form
    })

def home(request):
    return render(request, 'home.html')

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')