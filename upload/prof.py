from upload.forms import FileForm
from upload.models import File, Submission, Person, Course, GitHubAccount, Assignment
from upload.utils import *

from datetime import datetime
import os.path
import sys
import pytz
from pytz import timezone

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect

from github import GithubException
from git import Git

HISTORY_LENGTH = 5



@login_required
def create_assignment(request, course_id):
    course = Course.objects.get(id = course_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        #TODO: time zones
        central = timezone('US/Central')
        due_date = central.localize(datetime.strptime(request.POST.get('due_date'), '%Y-%m-%dT%H:%M'))
        try:
            ## TODO: you can select any course, even ones you are not the prof of
            assignment = Assignment(title=title, description=description, course=course, deadline=due_date)
            assignment.save()
        except Exception as e:
            print(e)
            return redirect('/error')
        return redirect('/prof/')
    return render(request,
                  'upload/prof/create_assignment.html',{'course':course})

@login_required
def edit_assignment(request, course_id, assignment_id):
    assignment = Assignment.objects.get(pk=assignment_id)
    course = Course.objects.get(pk=course_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        #TODO: time zones
        central = timezone('US/Central')
        due_date = central.localize(datetime.strptime(request.POST.get('due_date'), '%Y-%m-%dT%H:%M'))
        try:
            #assignment = Assignment(title=title, description=description, course=course, deadline=due_date)
            assignment.title=title
            assignment.description=description
            assignment.course=course
            assignment.deadline=due_date
            assignment.save()
        except Exception as e:
            print(e)
            return redirect('/error')
        return redirect('/prof/courses/{0}/{1}/assignment_description'.format(course.id,assignment.id))
    return render (request, 'upload/prof/edit_assignment.html', {'assignment': assignment, 'course': course})

@login_required
def assignment_description(request, course_id, assignment_id):
    assignment = Assignment.objects.get(pk=assignment_id)
    if request.method == 'POST':
        #TODO Delete already submitted assignments
        assignment.delete()
        return redirect('/prof/courses/{0}'.format(course_id))
    course = Course.objects.get(pk=course_id)
    return render(request, 'upload/prof/assignment_description.html', {'assignment': assignment, 'course': course})



@login_required
def create_course(request):
    if request.method == 'POST':
        course_number= request.POST.get('course_number')
        section = request.POST.get('section')
        title = request.POST.get('title')
        term = request.POST.get('term')
        id = '{0}.{1}-{2}'.format(course_number.replace(' ', '-'), section, term)
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
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('/prof/courses/')

    username = request.user.username
    assignments = Assignment.objects.filter(course__id=course_id).order_by('deadline')

    submissions_items = get_submission_items(username, course_id, None)
    # TODO: display variable length history (GUI toggle like in Moodle?)
    return render(request, 'upload/prof/course.html', {
        'submissions': submissions_items[:HISTORY_LENGTH],
        'course': course,
        'assignments': assignments
    })

@login_required
def assign_grader(request, course_id):
    course = Course.objects.get(id = course_id)
    if request.method == 'POST':
        grader_username = request.POST.get('username')
        grader = Person.objects.get(pk=username)
    return render(request, 'upload/prof/assign_grader.html', {'course':course})
