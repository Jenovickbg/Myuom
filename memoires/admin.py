from django.contrib import admin
from .models import Memoire, CertificatMemoire


@admin.register(Memoire)
class MemoireAdmin(admin.ModelAdmin):
    list_display = ['titre', 'etudiant', 'domaine', 'statut', 'directeur', 'date_soumission_sujet']
    list_filter = ['statut', 'domaine', 'plagiat_verifie']
    search_fields = ['titre', 'etudiant__first_name', 'etudiant__last_name', 'etudiant__matricule']
    date_hierarchy = 'date_soumission_sujet'


@admin.register(CertificatMemoire)
class CertificatMemoireAdmin(admin.ModelAdmin):
    list_display = ['numero_certificat', 'memoire', 'date_emission', 'annee_academique']
    search_fields = ['numero_certificat', 'memoire__titre', 'memoire__etudiant__matricule']
    date_hierarchy = 'date_emission'



