from django.urls import path
from . import views

app_name = 'cours'

urlpatterns = [
    path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
    path('teacher/supports/create/', views.support_create, name='support_create'),
]


