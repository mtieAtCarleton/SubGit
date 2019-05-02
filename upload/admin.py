from django.contrib import admin
from upload.models import Course, Student, Submission, GitHubAccount, Assignment, File
# Register your models here.
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Submission)
admin.site.register(GitHubAccount)
admin.site.register(Assignment)
admin.site.register(File)