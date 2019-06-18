from django.shortcuts import render, redirect
from upload.forms import FileForm
from upload.models import File, Submission, Student, Course, GitHubAccount, Assignment
import os.path
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from github import GithubException
from git import Git
import sys
from upload.utils import *
from django.http import JsonResponse

HISTORY_LENGTH = 5


@login_required
def courses(request):
    user_directory = os.path.join(MEDIA_ROOT, request.user.username)
    if os.path.exists(user_directory):
        try:
            return render(request, 'upload/courses.html', {
                 'courses': Student.objects.get(username=request.user.username).courses.all()
             })
        except Student.DoesNotExist as e:
            return redirect('/register/')
    else:
        return redirect('/register/')


@login_required
def course(request, course_id):
    username = request.user.username
    submissions_items = get_submission_items(username, course_id, None)

    assignments = Assignment.objects.filter(course__id=course_id).order_by('deadline')

    # TODO: display variable length history (GUI toggle like in Moodle?)
    return render(request, 'upload/course.html', {
        'submissions': submissions_items[:HISTORY_LENGTH],
        'course': Course.objects.get(id=course_id),
        'assignments': assignments
    })


@login_required
def upload_assignment(request, course_id, assignment_id):
    username = request.user.username
    course_directory = os.path.join(MEDIA_ROOT, username, course_id)
    pending_submissions = File.objects.filter(submission__isnull=True, student__username=username,
                                              assignment__id=assignment_id)

    if Assignment.objects.filter(id=assignment_id).exists():
        assignment = Assignment.objects.get(id=assignment_id)
        assignment_title = assignment.title.replace(' ', '_')
    else:
        assignment, assignment_title = None, None

    if request.method == 'POST':
        if "clear" in request.POST:
            # if a file was cleared out of the upload box, remove it from the pending submissions and delete it
            file_id = request.POST["clear"]
            file = File.objects.get(id=file_id)
            # check to make sure the same file isn't being submitted for another assignment before deleting it
            clear_file(assignment_id, file, username)
            pending_submissions.exclude(file=file)
            form = FileForm()
        elif "submit" in request.POST:
            # if the form is ready to submit, make a new submission entry in the database with the current pending files
            # then add to Git, commit and push to GitHub
            if pending_submissions:
                commit_message = request.POST["description"]
                submission = Submission.objects.create(description=commit_message, assignment=assignment)

                file_paths = []
                for file in pending_submissions:
                    file_paths.append(os.path.join(MEDIA_ROOT, file.file.name))
                    file.submission = submission
                    file.save()

                submit(username, course_id, file_paths, commit_message, assignment_title)

                return redirect('/submitted/{}/{}'.format(course_id, assignment_id))
            else:
                form = FileForm()
        else:
            # if a file was uploaded but not submitted yet, save it to the database and return its data so the
            # JavaScript can display it in the upload box
            form = FileForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save(commit=False)
                file.student = Student.objects.get(username=username)
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
            print(e)
            return redirect('/error/')

    if Assignment.objects.filter(id=assignment_id).exists():
        assignment = Assignment.objects.get(id=assignment_id)
    else:
        assignment = None

    submissions_items = get_submission_items(username, course_id, assignment_id)

    # if a submission has been made, a branch corresponding to the assignment will have been created, so link to it.
    # otherwise, link to the main github page
    if submissions_items:
        url = get_branch_url(repo_name, assignment_title)
    else:
        url = get_github_url(repo_name)

    return render(request, 'upload/upload.html', {
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
    return render(request, 'upload/submitted.html', {
        'course_id': course_id,
        'url': get_branch_url(repo_name, assignment.title),
        'assignment': assignment,
        'submissions': submissions_items[:HISTORY_LENGTH]
    })


def home(request):
    if request.user.username:
        return redirect("/courses/")
    return render(request, 'upload/home.html')


def login_error(request):
    return render(request, 'upload/login_error.html')


def error(request):
    return render(request, 'upload/error.html')


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')


@login_required
def register(request):
    if request.method == 'POST':
        username = request.user.username

        course_id = request.POST.get('course-id')
        course, new = Course.objects.get_or_create(id=course_id)
        if new:
            course.save()

        student, new = Student.objects.get_or_create(username=username)
        if not student.courses.filter(id=course_id).exists():
            student.courses.add(course)
            student.save()

        user_directory = os.path.join(MEDIA_ROOT, username, course_id)

        if os.path.isdir(user_directory):
            return redirect('/courses/')
        try:
            os.makedirs(user_directory)
        except OSError:
            print(e)
            return redirect("/error")

        g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))
        repo_name = "{}-{}".format(course_id, username)

        # TODO: create within organization?
        try:
            repo = g.get_user().create_repo(repo_name, private=True)
        except GithubException as e:
            print(e)
            return redirect("/error")

        # TODO: break up this try block, improve error handling
        try:
            github_accounts = Student.objects.get(username=username).github_accounts.all()
            for account in github_accounts:
                repo.add_to_collaborators(account.username, "push")

            repo_url = "git@github.com:{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)

            # TODO: move to environment variable
            # see https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
            git_ssh_identity_file = os.path.expanduser(config('SSH_KEY_PATH'))
            git_ssh_cmd = "ssh -i {}".format(git_ssh_identity_file)

            with Git(user_directory).custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                local_repo = Repo.clone_from(repo_url, user_directory)

            readme_path = make_readme(username, user_directory)
            # TODO: override any existing git config of username/password and use SubGitAdmin instead
            local_repo.index.add([readme_path])
            local_repo.index.commit("Initial commit")
            origin = local_repo.remotes.origin
            origin.push()

            return redirect('/courses/')
        except Exception as e:
            print(e)
            print("Unexpected error:", sys.exc_info()[0])
            return redirect('/error/')

    if request.user.is_authenticated:
        student, new = Student.objects.get_or_create(username=request.user.username)
        return render(request, 'upload/register.html', {
            'courses': [course for course in Course.objects.all() if course not in student.courses.all()]
        })
    else:
        return render(request, 'upload/register.html', {
            'courses': Course.objects.all()
        })


@login_required
def registered(request):
    return render(request, 'upload/registered.html')


def not_registered(request):
    return render(request, 'upload/not_registered.html')


@login_required
def connect_github(request):
    if request.method == 'POST':
        input_username = request.POST.get('username')
        student = Student.objects.get(username=request.user.username)

        if input_username != config('GITHUB_ADMIN_USERNAME') and \
                not student.github_accounts.filter(username=input_username).exists():
            g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))

            account, new = GitHubAccount.objects.get_or_create(username=input_username)
            student.github_accounts.add(account)
            student.save()

            try:
                for course in student.courses.all():
                    repo_name = "{}-{}".format(course.id, request.user.username)
                    repo = g.get_user().get_repo(repo_name)
                    repo.add_to_collaborators(input_username, "push")
            except GithubException as e:
                print(e)
                account.delete()
                return redirect('/error')

            return redirect("/courses/")

    return render(request, "upload/connect_github.html")


@login_required
def manage_github(request):
    if request.method == "POST":
        account = request.POST.get('account')
        Student.objects.get(username=request.user.username).github_accounts.remove(account)

        g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))

        student = Student.objects.get(username=request.user.username)

        for course in student.courses.all():
            repo_name = "{}-{}".format(course.id, request.user.username)
            repo = g.get_user().get_repo(repo_name)
            try:
                repo.remove_from_collaborators(account)
            except GithubException as e:
                print(e)

    accounts = Student.objects.get(username=request.user.username).github_accounts.all()
    return render(request, 'upload/manage_github.html', {
        'accounts': accounts
    })


def carleton_test(backend, response, social, *args, **kwargs):
    email = response.get("email")
    if email.split("@")[1] != "carleton.edu":
        return redirect("/error")
