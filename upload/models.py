from django.db import models
import os
from SubGit.settings import MEDIA_ROOT


def content_file_name(instance, filename):
    """Returns the path to upload the given File instance and name, overwriting the current file at that path (if any).
       Should only be called when a File object is initialized.
    """
    filename = os.path.join(instance.student.username, instance.assignment.course.id, filename)
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


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    deadline = models.DateTimeField(null=True, blank=True)


class Submission(models.Model):
    class Meta:
        ordering = ["-submitted_at"]
    description = models.CharField(max_length=255, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True)

#TODO: think more carefully about on_delete, nulls
#TODO: should file know about assignment? if not, need a submitted bool in Submission to handle pending uploads
class File(models.Model):
    file = models.FileField(upload_to=content_file_name, null=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
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