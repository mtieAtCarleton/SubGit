from upload.forms import FileForm
from upload.models import Assignment, Course, Person, Submission
from upload.utils import get_submission_items, hredirect, hrender, grader_required

import os.path

from github import Github, GithubException
from git import Git

HISTORY_LENGTH = 5


@grader_required
def courses(request):
    print("hello world")
    grader = Person.objects.get(pk=request.user.username)
    courses = Course.objects.filter(graders__in=[grader]).all()
    return hrender(request, 'upload/grader/courses.html', {'courses': courses})


@grader_required
def course(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        '''figure out what to do in this instance'''

    username = request.user.username
    assignments = Assignment.objects.filter(course__id=course_id).order_by('deadline')

    submissions_items = get_submission_items(username, course_id, None)
    # TODO: display variable length history (GUI toggle like in Moodle?)
    return hrender(request, 'upload/grader/course.html', {
        'submissions': submissions_items[:HISTORY_LENGTH],
        'course': course,
        'assignments': assignments
    })


@grader_required
def assignment_submissions(request, course_id, assignment_id):
    course = Course.objects.get(id=course_id)
    assignment = Assignment.objects.get(id=assignment_id)
    students = Person.objects.filter(courses__in=(course_id,)).all()
    submission_items = []
    for student in students:
        submission_items.extend(get_submission_items(username=student.username,
                                                     course_id=course_id,
                                                     assignment_id=assignment_id))
    return hrender(request, 'upload/grader/assignment_submissions.html', {
                   'submissions': submission_items[:HISTORY_LENGTH],
                   'course': course,
                   'assignment': assignment
                   })
