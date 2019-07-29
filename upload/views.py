from upload.forms import FileForm
from upload.models import Assignment, Course, Error, File, GitHubAccount, Person, Submission
from SubGit.settings import MEDIA_ROOT
from upload.utils import add_student_to_course, clear_file, config, hredirect, hrender, submit, make_error
from upload.utils import get_github_repo, get_github_url, get_branch_url, get_submission_items, give_github_permissions, clone_course_repo
import os.path
import threading

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from git import Git
from github import Github, GithubException

HISTORY_LENGTH = 5


@login_required
def clear_error(request, username):
    errors = Error.objects.filter(user__username=username)
    if errors.exists():
        errors.delete()
    path = request.GET.get('q')
    print('Path', path)
    return hredirect(request, path)


@login_required
def courses(request):
    username = request.user.username
    if Person.objects.filter(username=username).exists():
        person = Person.objects.get(username=username)
        return hrender(request,
                       'upload/courses.html',
                       {'courses': person.courses.all()},
                       person)
    else:
        return hredirect(request, '/register/')


@login_required
def course(request, course_id):
    username = request.user.username
    course = Course.objects.get(id=course_id)
    # TODO: think about deleting github repos
    if request.method == 'POST':
        student = Person.objects.get(username=username)
        student.courses.remove(course)
        student.save()
        return hredirect(request, '/courses/', person=student)

    submissions_items = get_submission_items(username, course_id, None)

    assignments = Assignment.objects.filter(course__id=course_id).order_by('deadline')

    # TODO: display variable length history
    # (GUI toggle like in Moodle?)
    return hrender(request, 'upload/course.html', {
        'submissions': submissions_items[:HISTORY_LENGTH],
        'course': course,
        'assignments': assignments
    })


@login_required
def upload_assignment(request, course_id, assignment_id):
    username = request.user.username
    course_directory = os.path.join(MEDIA_ROOT, username, course_id)
    pending_submissions = File.objects.filter(submission__isnull=True, person__username=username,
                                              assignment__id=assignment_id)

    if Assignment.objects.filter(id=assignment_id).exists():
        assignment = Assignment.objects.get(id=assignment_id)
        assignment_title = assignment.title.replace(' ', '_')
    else:
        assignment, assignment_title = None, None

    if request.method == 'POST':
        if "clear" in request.POST:
            # if a file was cleared out of the upload box, remove it
            # from the pending submissions and delete it
            file_id = request.POST["clear"]
            file = File.objects.get(id=file_id)
            # check to make sure the same file isn't being submitted
            # for another assignment before deleting it
            clear_file(assignment_id, file, username)
            pending_submissions.exclude(file=file)
            form = FileForm()
        elif "submit" in request.POST:

            # if the form is ready to submit, make a new submission entry
            # in the database with the current pending files
            # then add to Git, commit and push to GitHub
            if pending_submissions:
                commit_message = request.POST["description"]
                submission = Submission.objects.create(description=commit_message,
                                                       assignment=assignment)

                file_paths = []
                for file in pending_submissions:
                    file_paths.append(os.path.join(MEDIA_ROOT, file.file.name))
                    file.submission = submission
                    file.save()

                submit(username, course_id, file_paths, commit_message, assignment_title)

                return hredirect(request, '/submitted/{}/{}'.format(course_id, assignment_id))
            else:
                form = FileForm()
        else:
            # if a file was uploaded but not submitted yet,
            # save it to the database and return its data so the
            # JavaScript can display it in the upload box
            form = FileForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save(commit=False)
                file.person = Person.objects.get(username=username)
                file.assignment = Assignment.objects.get(id=assignment_id)
                file.save()
                data = {'is_valid': True, 'name': file.file.name, 'url': file.file.url, 'id': file.id}
            else:
                data = {'is_valid': False}
            return JsonResponse(data)
    # if no file is being uploaded, display an empty form
    else:
        form = FileForm()

    repo_directory = os.path.join(course_directory, ".git")
    repo_name = "{}-{}".format(course_id, username)

    if not os.path.exists(repo_directory):
        try:
            clone_course_repo(course_id, repo_name, username)
        except GithubException as e:
            make_error(username, 'Could not upload due to ' + e)
            return hredirect(request, '/upload/{0}/{1}'.format(course_id, assignment_id))

    if Assignment.objects.filter(id=assignment_id).exists():
        assignment = Assignment.objects.get(id=assignment_id)
    else:
        assignment = None

    submissions_items = get_submission_items(username, course_id, assignment_id)

    # if a submission has been made, a branch corresponding
    # to the assignment will have been created, so link to it.
    # otherwise, link to the main github page
    if submissions_items:
        url = get_branch_url(repo_name, assignment_title)
    else:
        url = get_github_url(repo_name)

    return hrender(request, 'upload/upload.html', {
        'form': form,
        'course': Course.objects.get(id=course_id),
        'url': url,
        'pending': pending_submissions,
        'assignment': assignment,
        'submissions': submissions_items[:HISTORY_LENGTH]
    })


@login_required
def submitted(request, course_id, assignment_id):
    username = request.user.username
    repo_name = "{}-{}".format(course_id, username)
    if Assignment.objects.filter(id=assignment_id).exists():
        assignment = Assignment.objects.get(id=assignment_id)
        submissions_items = get_submission_items(username, course_id, assignment_id)
    else:
        assignment = None
        submissions_items = None
    return hrender(request, 'upload/submitted.html', {
        'course_id': course_id,
        'url': get_branch_url(repo_name, assignment.title),
        'assignment': assignment,
        'submissions': submissions_items[:HISTORY_LENGTH]
    })


def home(request, next=''):
    if request.user.username:
        return hredirect(request, "/courses/")
    return hrender(request, 'upload/home.html')


def login_error(request):
    return hrender(request, 'upload/login_error.html')


def error(request):
    return hrender(request, 'upload/error.html')


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return hredirect(request, '/')


@login_required
def register(request):
    if request.method == 'POST':
        # Create user if not exists (done here since it is the main redirect)
        username = request.user.username
        person = Person.objects.get(username=username)

        course_id = request.POST.get('course-id')

        try:
            course = Course.objects.get(id=course_id)
        except ObjectDoesNotExist:
            make_error(username, 'Course does not exist')
            return hredirect(request, '/register')

        # If person is not registered for the course
        if not person.courses.filter(id=course_id).exists():
            person.courses.add(course)
            person.save()

        target = threading.Thread(target=add_student_to_course,
                                  args=(username, course_id),
                                  daemon=True)
        target.start()
        return hredirect(request, '/courses')

    if request.user.is_authenticated:
        person = Person.objects.get(username=request.user.username)
        return hrender(request, 'upload/register.html', {
            'courses': [course for course in Course.objects.all() if course not in person.courses.all()]
        })
    else:
        return hrender(request, 'upload/register.html', {
            'courses': Course.objects.all()
        })


@login_required
def registered(request):
    return hrender(request, 'upload/registered.html')


def not_registered(request):
    return hrender(request, 'upload/not_registered.html')


@login_required
def connect_github(request):
    if request.method == 'POST':
        username = request.user.username
        github_username = request.POST.get('username')
        person = Person.objects.get(username=username)

        if github_username != config('GITHUB_ADMIN_USERNAME') and \
                not person.github_accounts.filter(username=github_username).exists():
            account = GitHubAccount(username=github_username)
            account.save()
            person.github_accounts.add(account)
            person.save()

            try:
                for course in person.courses.all():
                    repo = get_github_repo(username, course.id)
                    give_github_permissions(person, repo, "push")
            except GithubException as e:
                make_error(username, e)
                account.delete()
                return hredirect(request, '/connect_github')

            return hredirect(request, "/manage_github/")

    return hrender(request, "upload/connect_github.html")


@login_required
def manage_github(request):
    if request.method == "POST":
        account = request.POST.get('account')
        Person.objects.get(username=request.user.username).github_accounts.remove(account)

        g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))

        person = Person.objects.get(username=request.user.username)

        for course in person.courses.all():
            repo_name = "{}-{}".format(course.id, request.user.username)
            repo = g.get_user().get_repo(repo_name)
            try:
                repo.remove_from_collaborators(account)
            except GithubException as e:
                print(e)

    accounts = Person.objects.get(username=request.user.username).github_accounts.all()
    return hrender(request, 'upload/manage_github.html', {
        'accounts': accounts
    })
