from django.urls import path
from . import views

app_name = 'travaux'

urlpatterns = [
    # URLs pour enseignants
    path('teacher/travaux/', views.teacher_travaux_list, name='teacher_travaux_list'),
    path('teacher/cours/selection/', views.teacher_cours_selection, name='teacher_cours_selection'),
    path('teacher/cours/<int:cours_id>/travail/create/', views.teacher_travail_create, name='teacher_travail_create'),
    path('teacher/travaux/<int:travail_id>/', views.teacher_travail_detail, name='teacher_travail_detail'),
    path('teacher/travaux/<int:travail_id>/toggle/', views.teacher_travail_toggle_status, name='teacher_travail_toggle_status'),
    path('teacher/remises/<int:remise_id>/', views.teacher_remise_detail, name='teacher_remise_detail'),
    
    # URLs pour étudiants
    path('student/travaux/<int:travail_id>/rendre/', views.student_rendre_travail, name='student_rendre_travail'),
]


