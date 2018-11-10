from django.db import models
import os

gitUsername = ''


def content_file_name(instance, filename):
    return os.path.join('%s/' % gitUsername, filename)


class Course(models.Model):
    # students = models.ManyToManyField(Student)
    id = models.CharField(max_length=30, primary_key=True, unique=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    prof = models.CharField(max_length=255, null=True, blank=True)


class Student(models.Model):
    username = models.CharField(max_length=30, primary_key=True, unique=True)
    courses = models.ManyToManyField(Course)


class Submission(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=content_file_name, null=False, verbose_name="")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #student = models.ForeignKey(Student, on_delete=models.CASCADE)
