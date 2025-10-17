from django.urls import path
from . import views

app_name = 'memoires'

urlpatterns = [
    # URLs pour étudiants
    path('student/dashboard/', views.student_memoire_dashboard, name='student_memoire_dashboard'),
    path('student/soumettre-sujet/', views.student_soumettre_sujet, name='student_soumettre_sujet'),
    path('student/deposer-memoire/', views.student_deposer_memoire, name='student_deposer_memoire'),
    path('student/verifier-plagiat/', views.student_verifier_plagiat, name='student_verifier_plagiat'),
    path('student/confirmer-final/', views.student_confirmer_final, name='student_confirmer_final'),
    path('student/telecharger-certificat/', views.student_telecharger_certificat, name='student_telecharger_certificat'),
    
    # URLs pour admin
    path('admin/memoires/', views.admin_memoires_list, name='admin_memoires_list'),
    path('admin/memoires/<int:memoire_id>/valider/', views.admin_valider_memoire, name='admin_valider_memoire'),
]



