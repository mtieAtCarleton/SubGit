from django.db import models
import os
from SubGit.settings import MEDIA_ROOT


def content_file_name(instance, filename):
    filename = os.path.join(instance.student.username, instance.course.id, filename)
    filepath = os.path.join(MEDIA_ROOT, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return filename


class Course(models.Model):
    # students = models.ManyToManyField(Student)
    id = models.CharField(max_length=30, primary_key=True, unique=True)
    number = models.CharField(max_length=15, null=True, blank=True)
    section = models.CharField(max_length=3, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    prof = models.CharField(max_length=255, null=True, blank=True)


class GitHubAccount(models.Model):
    username = models.CharField(max_length=255, primary_key=True, unique=True)

#TODO: make GitHub accounts many-to-one
class Student(models.Model):
    username = models.CharField(max_length=30, primary_key=True, unique=True)
    courses = models.ManyToManyField(Course)
    #github_username = models.CharField(max_length=255, null=True, blank=True)
    github_accounts = models.ManyToManyField(GitHubAccount)


class Submission(models.Model):
    description = models.CharField(max_length=255, blank=True)

#TODO: think more carefully about on_delete, nulls
class File(models.Model):
    file = models.FileField(upload_to=content_file_name, null=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, null=True)

# class Submission(models.Model):
#     description = models.CharField(max_length=255, blank=True)
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#
#
# class File(models.Model):
#     file = models.FileField(upload_to=content_file_name, null=False)
#     submission = models.ForeignKey(Submission, on_delete=models.CASCADE, null=True)