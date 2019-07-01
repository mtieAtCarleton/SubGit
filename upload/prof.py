from upload.models import Person, Course, Assignment
from upload.utils import get_submission_items, hredirect, hrender, prof_required

from datetime import datetime
from pytz import timezone

from django.contrib.auth.decorators import login_required

HISTORY_LENGTH = 5


@prof_required
def create_assignment(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        # TODO: time zones
        central = timezone('US/Central')
        due_date = central.localize(datetime.strptime(request.POST.get('due_date'),
                                                      '%Y-%m-%dT%H:%M'))
        try:
            # TODO: you can select any course, even ones you are not the prof of
            assignment = Assignment(title=title,
                                    description=description,
                                    course=course,
                                    deadline=due_date)
            assignment.save()
        except Exception as e:
            print(e)
            return hredirect(request, '/error')
        return hredirect(request, '/prof/')
    return hrender(request,
                   'upload/prof/create_assignment.html', {'course': course})


@prof_required
def edit_assignment(request, course_id, assignment_id):
    assignment = Assignment.objects.get(pk=assignment_id)
    course = Course.objects.get(pk=course_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        # TODO: time zones
        central = timezone('US/Central')
        due_date = central.localize(datetime.strptime(request.POST.get('due_date'),
                                                      '%Y-%m-%dT%H:%M'))
        try:
            assignment.title = title
            assignment.description = description
            assignment.course = course
            assignment.deadline = due_date
            assignment.save()
        except Exception as e:
            print(e)
            return hredirect(request, '/error')
        return hredirect(request, '/prof/courses/{0}/{1}/assignment_description'.format(course.id, assignment.id))
    return hrender(request,
                   'upload/prof/edit_assignment.html',
                   {'assignment': assignment, 'course': course})


@prof_required
def assignment_description(request, course_id, assignment_id):
    assignment = Assignment.objects.get(pk=assignment_id)
    if request.method == 'POST':
        # TODO: Delete already submitted assignments
        assignment.delete()
        return hredirect(request, '/prof/courses/{0}'.format(course_id))
    course = Course.objects.get(pk=course_id)
    return hrender(request,
                   'upload/prof/assignment_description.html',
                   {'assignment': assignment, 'course': course})


@prof_required
def create_course(request):
    if request.method == 'POST':
        course_number = request.POST.get('course_number')
        section = request.POST.get('section')
        title = request.POST.get('title')
        term = request.POST.get('term')
        id = '{0}.{1}-{2}'.format(course_number.replace(' ', '-'), section, term)
        prof = Person.objects.get(pk=request.user.username)
        try:
            # TODO: check for course existence
            course = Course(id=id, number=course_number,
                            title=title, section=section, prof=prof)
            course.save()
        except Exception as e:
            print(e)
            return hredirect(request, '/error', person=prof)
        return hredirect(request, '/prof', person=prof)
    return hrender(request, 'upload/prof/create_course.html')


def home(request):
    if request.user.username:
        return hredirect(request, "/prof/courses/")
    return hrender(request, 'upload/home.html')


@prof_required
def courses(request):
    prof = Person.objects.get(pk=request.user.username)
    courses = Course.objects.filter(prof__exact=prof).all()
    return hrender(request, 'upload/prof/courses.html', {'courses': courses}, person=prof)


@prof_required
def course(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        course.delete()
        return hredirect(request, '/prof/courses/')

    username = request.user.username
    assignments = Assignment.objects.filter(course__id=course_id).order_by('deadline')

    submissions_items = get_submission_items(username, course_id, None)
    # TODO: display variable length history (GUI toggle like in Moodle?)
    return hrender(request, 'upload/prof/course.html', {
        'submissions': submissions_items[:HISTORY_LENGTH],
        'course': course,
        'assignments': assignments
    })


@prof_required
def assign_grader(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        grader_username = request.POST.get('grader_username')
        try:
            grader = Person.objects.get(pk=grader_username)
            course.grader = grader
            course.save()
        except Exception as e:
            print(e)
            return hredirect('/error')
    return hrender(request, 'upload/prof/assign_grader.html', {'course': course})

@login_required
def delete_grader(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        grader_username = request.POST.get('grader_username')
        try:
            grader = Person.objects.get(pk=grader_username)
            grader.delete()
        except Exception as e:
            print(e)
            return hredirect('/error')
    return hrender(request, 'upload/prof/delete_grader.html', {'course': course})
