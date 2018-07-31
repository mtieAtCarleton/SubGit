from django.db import models

# Create your models here.
from django.db import models
import os

gitUsername = ''

def content_file_name(instance, filename):
    return os.path.join('uploads/%s/' % gitUsername, filename)

class Submission(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=content_file_name, null=False, verbose_name="File")
    uploaded_at = models.DateTimeField(auto_now_add=True)

