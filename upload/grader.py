from upload.forms import FileForm
from upload.models import *
from upload.utils import *

import os.path
import sys
import threading

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from github import GithubException
from git import Git

HISTORY_LENGTH = 5


@login_required
def courses(request):
    print("hello world")
    grader = Person.objects.get(pk=request.user.username)
    courses = Course.objects.filter(grader__exact=grader).all()
    return hrender(request, 'upload/grader/courses.html', {'courses': courses})
