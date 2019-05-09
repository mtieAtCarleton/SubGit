"""SubGit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #path('upload/<str:course_id>', views.model_form_upload,
    #     name='model_form_upload'),
    path('upload/<str:course_id>/<str:assignment_id>', views.upload_assignment, name='upload_assignment'),
    path('', views.home),
    path('logout/', views.logout),
    path('submitted/<str:course_id>/<str:assignment_id>', views.submitted),
    path('not_registered/', views.not_registered),
    path('register/', views.register),
    path('registered/', views.registered),
    path('error/', views.error),
    path('courses/', views.courses),
    path('connect_github/', views.connect_github),
    path('manage_github/', views.manage_github),
    path('login_error/', views.login_error),
    path('history/<str:course_id>', views.history),
    path('courses/<str:course_id>', views.course)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
