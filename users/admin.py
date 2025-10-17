from django.contrib import admin
from .models import CustomUser, StudentProfile, TeacherProfile, Faculte, Promotion, FraisAcademique

@admin.register(FraisAcademique)
class FraisAcademiqueAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'annee_academique', 'montant_total', 'montant_paye', 'montant_restant', 'statut', 'date_paiement']
    list_filter = ['statut', 'annee_academique', 'mode_paiement']
    search_fields = ['etudiant__matricule', 'etudiant__first_name', 'etudiant__last_name', 'reference_paiement']
    readonly_fields = ['created_at', 'updated_at', 'pourcentage_paye']
    
    fieldsets = (
        ('Étudiant', {
            'fields': ('etudiant', 'annee_academique')
        }),
        ('Montants', {
            'fields': ('montant_total', 'montant_paye', 'pourcentage_paye', 'statut')
        }),
        ('Paiement', {
            'fields': ('date_paiement', 'mode_paiement', 'reference_paiement')
        }),
        ('Notes', {
            'fields': ('remarques',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
