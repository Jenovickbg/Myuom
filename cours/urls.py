from django.urls import path
from . import views

app_name = 'cours'

urlpatterns = [
    # Vues administrateur
    path('admin/cours/', views.admin_cours_list, name='admin_cours_list'),
    path('admin/cours/create/', views.admin_cours_create, name='admin_cours_create'),
    path('admin/cours/<int:cours_id>/data/', views.admin_cours_data, name='admin_cours_data'),
    path('admin/cours/<int:cours_id>/edit/', views.admin_cours_edit, name='admin_cours_edit'),
    path('admin/cours/<int:cours_id>/delete/', views.admin_cours_delete, name='admin_cours_delete'),
    path('admin/cours/<int:cours_id>/toggle-active/', views.admin_cours_toggle_active, name='admin_cours_toggle_active'),
    
    # Vues enseignant
    path('teacher/cours/', views.teacher_cours_list, name='teacher_cours_list'),
    path('teacher/cours/<int:cours_id>/', views.teacher_cours_detail, name='teacher_cours_detail'),
    path('teacher/cours/create/', views.teacher_cours_create, name='teacher_cours_create'),
    
    # Vues étudiant
    path('student/cours/', views.student_cours_list, name='student_cours_list'),
    path('student/cours/<int:cours_id>/', views.student_cours_detail, name='student_cours_detail'),
    path('student/cours/<int:cours_id>/inscription/', views.student_cours_inscription, name='student_cours_inscription'),
]