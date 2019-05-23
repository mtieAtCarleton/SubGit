from django.contrib import admin
from upload.models import Course, Student, Submission, GitHubAccount, Assignment, File
# Register your models here if you want them to appear in the admin interface.
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Submission)
admin.site.register(GitHubAccount)
admin.site.register(Assignment)
admin.site.register(File)