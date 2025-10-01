from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Travail(models.Model):
    """
    Modèle pour les travaux (TP, TD, projets)
    """
    TYPE_TRAVAIL_CHOICES = [
        ('tp', 'Travaux Pratiques'),
        ('td', 'Travaux Dirigés'),
        ('projet', 'Projet'),
        ('examen', 'Examen'),
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('ferme', 'Fermé'),
        ('corrige', 'Corrigé'),
    ]
    
    # Informations de base
    titre = models.CharField(max_length=200, help_text="Titre du travail")
    description = models.TextField(help_text="Description du travail")
    consignes = models.TextField(help_text="Consignes pour les étudiants")
    
    # Classification
    type_travail = models.CharField(max_length=20, choices=TYPE_TRAVAIL_CHOICES, default='tp')
    niveau = models.CharField(max_length=5, choices=[
        ('L1', 'Licence 1'), ('L2', 'Licence 2'), ('L3', 'Licence 3'),
        ('M1', 'Master 1'), ('M2', 'Master 2')
    ])
    filiere = models.CharField(max_length=100, help_text="Filière concernée")
    
    # Enseignant responsable
    enseignant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='travaux_enseignant',
        limit_choices_to={'user_type': 'enseignant'}
    )
    
    # Dates importantes
    date_creation = models.DateTimeField(auto_now_add=True)
    date_publication = models.DateTimeField(null=True, blank=True, help_text="Date de publication")
    date_limite_remise = models.DateTimeField(help_text="Date limite de remise")
    date_limite_correction = models.DateTimeField(null=True, blank=True, help_text="Date limite de correction")
    
    # Paramètres
    note_maximale = models.DecimalField(max_digits=5, decimal_places=2, default=20.00, help_text="Note maximale")
    coefficient = models.DecimalField(max_digits=3, decimal_places=2, default=1.00, help_text="Coefficient")
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    is_visible_etudiants = models.BooleanField(default=True, help_text="Visible pour les étudiants")
    
    # Fichiers joints (consignes, ressources)
    fichier_consignes = models.FileField(
        upload_to='travaux/consignes/%Y/%m/',
        blank=True,
        null=True,
        help_text="Fichier de consignes (optionnel)"
    )
    
    class Meta:
        verbose_name = "Travail"
        verbose_name_plural = "Travaux"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.get_type_travail_display()}"
    
    def is_remise_ouverte(self):
        """Vérifie si la remise est encore ouverte"""
        if self.statut != 'publie':
            return False
        return timezone.now() <= self.date_limite_remise
    
    def is_correction_ouverte(self):
        """Vérifie si la correction est encore ouverte"""
        if self.statut not in ['publie', 'ferme']:
            return False
        if not self.date_limite_correction:
            return True
        return timezone.now() <= self.date_limite_correction


class RemiseTravail(models.Model):
    """
    Modèle pour les remises de travaux par les étudiants
    """
    STATUT_REMISE_CHOICES = [
        ('remis', 'Remis'),
        ('en_cours_correction', 'En cours de correction'),
        ('corrige', 'Corrigé'),
        ('note_finalisee', 'Note finalisée'),
    ]
    
    # Relations
    etudiant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='remises_etudiant',
        limit_choices_to={'user_type': 'etudiant'}
    )
    travail = models.ForeignKey(Travail, on_delete=models.CASCADE, related_name='remises')
    
    # Fichiers remis
    fichier_principal = models.FileField(
        upload_to='travaux/remises/%Y/%m/',
        help_text="Fichier principal du travail"
    )
    fichiers_supplementaires = models.FileField(
        upload_to='travaux/remises/%Y/%m/',
        blank=True,
        null=True,
        help_text="Fichiers supplémentaires (optionnel)"
    )
    
    # Commentaires
    commentaire_etudiant = models.TextField(blank=True, help_text="Commentaire de l'étudiant")
    commentaire_enseignant = models.TextField(blank=True, help_text="Commentaire de l'enseignant")
    
    # Dates
    date_remise = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # Statut
    statut = models.CharField(max_length=30, choices=STATUT_REMISE_CHOICES, default='remis')
    
    # Note et correction
    note = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Note obtenue"
    )
    date_correction = models.DateTimeField(null=True, blank=True, help_text="Date de correction")
    
    # Détection de plagiat
    score_plagiat = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score de similarité (0-100%)"
    )
    rapport_plagiat = models.TextField(blank=True, help_text="Rapport de détection de plagiat")
    
    class Meta:
        verbose_name = "Remise de travail"
        verbose_name_plural = "Remises de travaux"
        unique_together = ['etudiant', 'travail']
        ordering = ['-date_remise']
    
    def __str__(self):
        return f"{self.etudiant.matricule} - {self.travail.titre}"
    
    def is_en_retard(self):
        """Vérifie si la remise est en retard"""
        return self.date_remise > self.travail.date_limite_remise
    
    def get_statut_display_color(self):
        """Retourne la couleur CSS selon le statut"""
        colors = {
            'remis': 'primary',
            'en_cours_correction': 'warning',
            'corrige': 'success',
            'note_finalisee': 'info',
        }
        return colors.get(self.statut, 'secondary')
