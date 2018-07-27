
# Create your views here.
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from upload.forms import SubmissionForm
from SubGit.submit import submit
from upload.models import Submission
import os.path
import time

gitUsername = 'GalenWQ'

def model_form_upload(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            while not os.path.exists('/Accounts/bergerg/Desktop/SubGit/media/uploads/{}'.format(request.FILES['document'])):
                time.sleep(1)

            if os.path.isfile('/Accounts/bergerg/Desktop/SubGit/media/uploads/{}'.format(request.FILES['document'])):
                submit(gitUsername, request.FILES['document'])
            else:
                raise ValueError("isn't a file!")

            return redirect('/home/')
    else:
        form = SubmissionForm()
    return render(request, 'model_form_upload.html', {
        'form': form
    })

def home(request):
    return render(request, 'home.html')