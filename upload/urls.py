"""SubGit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views
from . import prof, grader
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/<str:course_id>/<str:assignment_id>',
         views.upload_assignment, name='upload_assignment'),
    path('', views.home),
    path('accounts/login/', views.home, name='next'),
    path('logout/', views.logout),
    path('submitted/<str:course_id>/<str:assignment_id>', views.submitted),
    path('not_registered/', views.not_registered),
    path('register/', views.register),
    path('registered/', views.registered),
    path('error/', views.error),
    path('login_error/', views.login_error),
    path('courses/', views.courses),
    path('courses/<str:course_id>', views.course),
    path('connect_github/', views.connect_github),
    path('manage_github/', views.manage_github),
    path('prof/', prof.home),
    path('prof/courses/', prof.courses),
    path('prof/courses/<str:course_id>', prof.course),
    path('prof/courses/<str:course_id>/<str:assignment_id>/edit_assignment', prof.edit_assignment),
    path('prof/courses/<str:course_id>/create_assignment', prof.create_assignment),
    path('prof/courses/<str:course_id>/<str:assignment_id>/assignment_description',
         prof.assignment_description),
    path('prof/courses/<str:course_id>/assign_grader', prof.assign_grader),
    path('prof/create_course/', prof.create_course),
    path('grader/courses/', grader.courses),
    path('grader/courses/<str:course_id>', grader.course)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# TODO: remove the static urls before deployment, find a better way to serve static files
