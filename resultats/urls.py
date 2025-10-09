from django.urls import path
from . import views

app_name = 'resultats'

urlpatterns = [
    # Vues étudiant
    path('student/resultats/', views.student_resultats, name='student_resultats'),
    path('student/bulletin/<int:bulletin_id>/pdf/', views.student_bulletin_pdf, name='student_bulletin_pdf'),
    
    # Vues admin
    path('admin/settings/', views.admin_resultats_settings, name='admin_resultats_settings'),
    path('admin/ues/', views.admin_ue_list, name='admin_ue_list'),
    path('admin/notes/', views.admin_notes_list, name='admin_notes_list'),
    path('admin/cotes/', views.admin_cotes_list, name='admin_cotes_list'),
    path('admin/cotes/generer/<int:etudiant_id>/', views.admin_generer_cote, name='admin_generer_cote'),
    path('admin/cotes/recalculer-tout/', views.admin_recalculer_toutes_cotes, name='admin_recalculer_toutes_cotes'),
]


