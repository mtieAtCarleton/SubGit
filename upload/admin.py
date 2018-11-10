from django.contrib import admin
from upload.models import Course, Student, Submission
# Register your models here.
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Submission)
