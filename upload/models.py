"""
This file defines the structure of the database where all of the webapp’s data is stored.
Every class represents a table in the database, and every class variable represents a column.

For more information see: https://docs.djangoproject.com/en/2.2/topics/db/models/
"""
from django.db import models
import os
from SubGit.settings import MEDIA_ROOT


def content_file_name(instance, filename):
    """Returns the path to upload the given File instance and name, overwriting the current file at that path (if any).
       Should only be called when a File object is initialized.
    """
    filename = os.path.join(instance.person.username, instance.assignment.course.id, filename)
    filepath = os.path.join(MEDIA_ROOT, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return filename


class Course(models.Model):
    # e.g. cs111.00-f18
    id = models.CharField(max_length=30, primary_key=True, unique=True)

    # e.g. cs111
    number = models.CharField(max_length=15, null=True, blank=True)

    # e.g. 00
    section = models.CharField(max_length=3, null=True, blank=True)

    # e.g. Introduction to Computer Science
    title = models.CharField(max_length=255, null=True, blank=True)

    # e.g. Eric Alexander
    prof = models.CharField(max_length=255, null=True, blank=True)


class GitHubAccount(models.Model):
    username = models.CharField(max_length=255, primary_key=True, unique=True)


# TODO: make GitHub accounts many-to-one
class Person(models.Model):
    username = models.CharField(max_length=30, primary_key=True, unique=True)
    courses = models.ManyToManyField(Course)
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


# TODO: think more carefully about on_delete, nulls
# TODO: should file know about assignment? if not, need a submitted bool in Submission to handle pending uploads
class File(models.Model):
    file = models.FileField(upload_to=content_file_name, null=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, null=True)

    def filename(self):
        return os.path.basename(self.file.name)
