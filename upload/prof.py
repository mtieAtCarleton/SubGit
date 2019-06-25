from upload.forms import FileForm
from upload.models import File, Submission, Person, Course, GitHubAccount, Assignment
from upload.utils import *

from datetime import datetime
import os.path
import sys

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect

from github import GithubException
from git import Git

HISTORY_LENGTH = 5



@login_required
def create_assignment(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        course_id = request.POST.get('course-id')
        #TODO: time zones
        due_date = datetime.strptime(request.POST.get('due_date'), '%Y-%m-%dT%H:%M')
        try:
            ## TODO: you can select any course, even ones you are not the prof of
            course = Course.objects.get(id = course_id)
            assignment = Assignment(title=title, course=course, deadline=due_date)
            assignment.save()
        except Exception as e:
            print(e)
            return redirect('/error')
        return redirect('/prof/')
    return render(request,
                  'upload/prof/create_assignment.html',
                  {'courses': list(Course.objects.all())})


@login_required
def create_course(request):
    if request.method == 'POST':
        course_number= request.POST.get('course_number')
        section = request.POST.get('section')
        title = request.POST.get('title')
        term = request.POST.get('term')
        id = '{0}.{1}-{2}'.format(course_number, section, term)
        prof = Person.objects.get(pk=request.user.username)
        try:
            #TODO check for course existence
            course = Course(id=id, number=course_number,
                            title=title, section=section, prof=prof)
            course.save()
        except Exception as e:
            print(e)
            return redirect('/error')
        return redirect('/prof')
    return render(request, 'upload/prof/create_course.html')


def home(request):
    if request.user.username:
        return redirect("/prof/courses/")
    return render(request, 'upload/home.html')


@login_required
def courses(request):
    prof = Person.objects.get(pk=request.user.username)
    courses = Course.objects.filter(prof__exact=prof).all()
    return render(request, 'upload/prof/courses.html', {'courses': courses})


@login_required
def course(request, course_id):
    username = request.user.username
    submissions_items = get_submission_items(username, course_id, None)
    course = Course.objects.get(id=course_id)
    print(course)
    assignments = Assignment.objects.filter(course__id=course_id).order_by('deadline')

    # TODO: display variable length history (GUI toggle like in Moodle?)
    return render(request, 'upload/prof/course.html', {
        'submissions': submissions_items[:HISTORY_LENGTH],
        'course': course,
        'assignments': assignments
    })
