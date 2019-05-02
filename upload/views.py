from django.shortcuts import render, redirect
from upload.forms import FileForm
from upload.models import File, Submission, Student, Course, GitHubAccount, Assignment
import os.path
from SubGit.settings import MEDIA_ROOT
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from github import Github
from github import GithubException
from decouple import config
from git import Repo
from git import Git
import sys
from upload.submit import submit
from django.http import JsonResponse


def handle_uploaded_file(f, file_path):
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

#TODO: refactor course and history
@login_required
def course(request, course_id):
    username = request.user.username
    files = File.objects.filter(submission__isnull=False, student__username=username, assignment__course__id=course_id)
    submissions = {}
    repo_name = "{}-{}".format(course_id, username)
    github_url = "https://github.com/{}/{}/blob".format(config("GITHUB_ADMIN_USERNAME"), repo_name)

    for file in files:
        filename = file.file.name.split('/')[-1]
        assignment = file.assignment.title.replace(" ", "_")
        url = "{}/{}/{}".format(github_url, assignment, filename)
        if file.submission in submissions:
            submissions[file.submission].append((file, url, filename))
        else:
            submissions[file.submission] = [(file, url, filename)]

    assignments = Assignment.objects.filter(course__id=course_id).order_by('deadline')

    return render(request, 'upload/course.html', {
        'submissions': submissions,
        'course': Course.objects.get(id=course_id),
        'assignments': assignments
    })

@login_required
def history(request, course_id):
    username = request.user.username
    files = File.objects.filter(submission__isnull=False, student__username=username, course__id=course_id)
    submissions = {}
    repo_name = "{}-{}".format(course_id, username)
    github_url = "https://github.com/{}/{}/blob/master/".format(config("GITHUB_ADMIN_USERNAME"), repo_name)
    for file in files:
        filename = file.file.name.split('/')[-1]
        url = github_url + filename
        if file.submission in submissions:
            submissions[file.submission].append((file, url, filename))
        else:
            submissions[file.submission] = [(file, url, filename)]

    return render(request, 'upload/history.html', {
        'submissions': submissions,
        'course': Course.objects.get(id=course_id),
    })


@login_required
def model_form_upload(request, course_id):
    upload_assignment(request, course_id, None)


@login_required
def upload_assignment(request, course_id, assignment_id):
    username = request.user.username
    course_directory = os.path.join(MEDIA_ROOT, username, course_id)
    pending_submissions = File.objects.filter(submission__isnull=True, student__username=username, assignment__id=assignment_id)

    if Assignment.objects.filter(id=assignment_id).exists():
        assignment = Assignment.objects.get(id=assignment_id)
        assignment_title = assignment.title.replace(' ', '_')
    else:
        assignment, assignment_title = None, None
    # if a file is being uploaded
    if request.method == 'POST':
        if "submit" in request.POST:
            #TODO: check for vulnerabilities
            commitMessage = request.POST["description"]
            submission = Submission.objects.create(description=commitMessage, assignment=assignment)

            file_paths = []
            for file in pending_submissions:
                file_paths.append(os.path.join(MEDIA_ROOT, file.file.name))
                file.submission = submission
                file.save()

            submit(username, course_id, file_paths, commitMessage, assignment_title)

            return redirect('/submitted/{}/{}'.format(course_id, assignment_id))
        else:
            form = FileForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save(commit=False)
                file.student = Student.objects.get(username=username)
                file.assignment = Assignment.objects.get(id=assignment_id)
                file.save()
                print("name: {}, url: {}".format(file.file.name, file.file.url))
                data = {'is_valid': True, 'name': file.file.name, 'url': file.file.url}
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

    return render(request, 'upload/upload.html', {
        'form': form,
        'course': Course.objects.get(id=course_id),
        'url': "https://github.com/{}/{}" \
                  .format(config("GITHUB_ADMIN_USERNAME"), repo_name),
        'pending': pending_submissions,
        'assignment': assignment
    })


def clone_course_repo(course_id, repo_name, username):
    g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))
    repo = g.get_user().get_repo(repo_name)
    repo_url = "git@github.com:{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)
    user_directory = os.path.join(MEDIA_ROOT, username, course_id)
    # TODO: move to environment variable
    git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
    git_ssh_cmd = "ssh -i {}".format(git_ssh_identity_file)
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        local_repo = Repo.clone_from(repo_url, user_directory)


def not_registered(request):
    return render(request, 'upload/not_registered.html')


def error(request):
    return render(request, 'upload/error.html')


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')


@login_required
def submitted(request, course_id, assignment_id):
    repo_name = "{}-{}".format(course_id, request.user.username)
    if Assignment.objects.filter(id=assignment_id).exists():
        assignment = Assignment.objects.get(id=assignment_id)
    else:
        assignment = None
    return render(request, 'upload/submitted.html', {
        'course_id': course_id,
        'url': "https://github.com/{}/{}/tree/{}".format(
            config("GITHUB_ADMIN_USERNAME"), repo_name, assignment.title.replace(" ", "_")),
        'assignment': assignment
    })


@login_required
def courses(request):
    user_directory = os.path.join(MEDIA_ROOT, request.user.username)
    if os.path.exists(user_directory):
        return render(request, 'upload/courses.html', {
            'courses': Student.objects.get(username=request.user.username).courses.all()
        })
    else:
        return redirect('/register/')


@login_required
def connect_github(request):
    if request.method == 'POST':
        input_username = request.POST.get('username')
        student = Student.objects.get(username=request.user.username)

        if input_username != config('GITHUB_ADMIN_USERNAME') and not student.github_accounts.filter(username=input_username).exists():
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
def register(request):
    if request.method == 'POST':
        username = request.user.username

        courseId = request.POST.get('course-id')
        course, new = Course.objects.get_or_create(id=courseId)
        if new:
            course.save()

        student, new = Student.objects.get_or_create(username=username)
        if not student.courses.filter(id=courseId).exists():
            student.courses.add(course)
            student.save()

        user_directory = os.path.join(MEDIA_ROOT, username, courseId)
        os.makedirs(user_directory)

        # TODO: break up this try block

        g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))
        repo_name = "{}-{}".format(courseId, username)

        try:
            repo = g.get_user().create_repo(repo_name)
        except GithubException as e:
            print(e)
            return redirect("/error")

        try:
            github_accounts = Student.objects.get(username=username).github_accounts.all()
            for account in github_accounts:
                repo.add_to_collaborators(account.username, "push")

            #repo_url = "https://github.com/{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)
            repo_url = "git@github.com:{}/{}.git".format(config("GITHUB_ADMIN_USERNAME"), repo_name)

            # TODO: move to environment variable
            git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
            git_ssh_cmd = "ssh -i {}".format(git_ssh_identity_file)

            with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                local_repo = Repo.clone_from(repo_url, user_directory)

            readme_path = make_readme(username, user_directory)

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


def make_readme(username, user_directory):
    readme_path = os.path.join(user_directory, "README.md")
    with open(readme_path, "w+") as readme:
        readme.write("Homework submission repository for {}".format(
            username))
        readme.close()
    return readme_path


@login_required
def registered(request):
    return render(request, 'upload/registered.html')


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


def home(request):
    if request.user.username:
        return redirect("/courses/")
    return render(request, 'upload/home.html')


def login_error(request):
    return render(request, 'upload/login_error.html')


def carleton_test(backend, response, social, *args, **kwargs):
    email = response.get("email")
    if email.split("@")[1] != "carleton.edu":
        return redirect("/error")