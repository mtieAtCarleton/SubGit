from django.db import models
import os

dir = ''


def content_file_name(instance, filename):
    return os.path.join('%s/' % dir, filename)


class Course(models.Model):
    # students = models.ManyToManyField(Student)
    id = models.CharField(max_length=30, primary_key=True, unique=True)
    number = models.CharField(max_length=15, null=True, blank=True)
    section = models.CharField(max_length=3, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    prof = models.CharField(max_length=255, null=True, blank=True)


class GitHubAccount(models.Model):
    username = models.CharField(max_length=255, primary_key=True, unique=True)


class Student(models.Model):
    username = models.CharField(max_length=30, primary_key=True, unique=True)
    courses = models.ManyToManyField(Course)
    #github_username = models.CharField(max_length=255, null=True, blank=True)
    github_accounts = models.ManyToManyField(GitHubAccount)


class Submission(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=content_file_name, null=False, verbose_name="")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #student = models.ForeignKey(Student, on_delete=models.CASCADE)


