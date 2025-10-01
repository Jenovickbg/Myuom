from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('first-login/password/', views.first_login_password_change, name='first_login_password_change'),
    path('first-login/profile/', views.first_login_profile_completion, name='first_login_profile_completion'),
    
    # Tableaux de bord
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/cours/', views.student_cours, name='student_cours'),
    path('student/travaux/', views.student_travaux, name='student_travaux'),
    path('student/resultats/', views.student_resultats, name='student_resultats'),
    path('student/profil/', views.student_profil, name='student_profil'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Gestion des étudiants (Admin)
    path('admin/students/', views.admin_student_list, name='admin_student_list'),
    path('admin/students/create/', views.admin_student_create, name='admin_student_create'),
    path('admin/students/<int:user_id>/', views.admin_student_detail, name='admin_student_detail'),
    path('admin/students/<int:user_id>/toggle-active/', views.admin_student_toggle_active, name='admin_student_toggle_active'),
    path('admin/students/<int:user_id>/reset-password/', views.admin_student_reset_password, name='admin_student_reset_password'),
    path('admin/students/bulk-import/', views.admin_student_bulk_import, name='admin_student_bulk_import'),
    
    # Gestion des enseignants (Admin)
    path('admin/teachers/', views.admin_teacher_list, name='admin_teacher_list'),
    path('admin/teachers/create/', views.admin_teacher_create, name='admin_teacher_create'),
    path('admin/teachers/<int:user_id>/', views.admin_teacher_detail, name='admin_teacher_detail'),
]


