
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

gitUsername = 'GalenWQ'

def model_form_upload(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            filePath = '{}/uploads/{}'.format(MEDIA_ROOT, request.FILES['document'])
            while not os.path.exists(filePath):
                time.sleep(1)

            if os.path.isfile(filePath):
                submit(gitUsername, request.FILES['document'])
            else:
                raise ValueError("isn't a file!")

            return redirect('')
    else:
        form = SubmissionForm()
    return render(request, 'model_form_upload.html', {
        'form': form
    })

def home(request):
    return render(request, 'home.html')