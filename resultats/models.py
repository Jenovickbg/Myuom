from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UE(models.Model):
    """
    Modèle pour les Unités d'Enseignement (UE)
    """
    NIVEAU_CHOICES = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
    ]
    
    SEMESTRE_CHOICES = [
        ('S1', 'Semestre 1'),
        ('S2', 'Semestre 2'),
        ('S3', 'Semestre 3'),
        ('S4', 'Semestre 4'),
        ('S5', 'Semestre 5'),
        ('S6', 'Semestre 6'),
        ('S7', 'Semestre 7'),
        ('S8', 'Semestre 8'),
        ('S9', 'Semestre 9'),
        ('S10', 'Semestre 10'),
    ]
    
    # Informations de base
    code = models.CharField(max_length=20, unique=True, help_text="Code de l'UE (ex: INFO101)")
    nom = models.CharField(max_length=200, help_text="Nom de l'UE")
    description = models.TextField(blank=True, help_text="Description de l'UE")
    
    # Classification
    niveau = models.CharField(max_length=5, choices=NIVEAU_CHOICES)
    semestre = models.CharField(max_length=5, choices=SEMESTRE_CHOICES)
    filiere = models.CharField(max_length=100, help_text="Filière concernée")
    
    # Paramètres
    credits = models.PositiveIntegerField(default=3, help_text="Nombre de crédits ECTS")
    coefficient = models.DecimalField(max_digits=3, decimal_places=2, default=1.00, help_text="Coefficient")
    
    # Enseignant responsable
    enseignant_responsable = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ues_responsable',
        limit_choices_to={'user_type': 'enseignant'}
    )
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateField(help_text="Date de début de l'UE")
    date_fin = models.DateField(help_text="Date de fin de l'UE")
    
    # Statut
    is_actif = models.BooleanField(default=True, help_text="UE active")
    is_visible_etudiants = models.BooleanField(default=True, help_text="Visible pour les étudiants")
    
    class Meta:
        verbose_name = "Unité d'Enseignement"
        verbose_name_plural = "Unités d'Enseignement"
        ordering = ['niveau', 'semestre', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"
    
    def get_display_name(self):
        return f"{self.code} - {self.nom}"


class Note(models.Model):
    """
    Modèle pour les notes des étudiants
    """
    TYPE_NOTE_CHOICES = [
        ('tp', 'Travaux Pratiques'),
        ('td', 'Travaux Dirigés'),
        ('examen', 'Examen'),
        ('projet', 'Projet'),
        ('participation', 'Participation'),
        ('autre', 'Autre'),
    ]
    
    # Relations
    etudiant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes_etudiant',
        limit_choices_to={'user_type': 'etudiant'}
    )
    ue = models.ForeignKey(UE, on_delete=models.CASCADE, related_name='notes')
    
    # Informations de la note
    type_note = models.CharField(max_length=20, choices=TYPE_NOTE_CHOICES, default='examen')
    titre = models.CharField(max_length=200, help_text="Titre de l'évaluation")
    description = models.TextField(blank=True, help_text="Description de l'évaluation")
    
    # Note
    note_obtenue = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Note obtenue"
    )
    note_maximale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.00,
        help_text="Note maximale"
    )
    coefficient = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        help_text="Coefficient de la note"
    )
    
    # Enseignant qui a donné la note
    enseignant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes_enseignant',
        limit_choices_to={'user_type': 'enseignant'}
    )
    
    # Dates
    date_evaluation = models.DateField(help_text="Date de l'évaluation")
    date_publication = models.DateTimeField(default=timezone.now, help_text="Date de publication de la note")
    
    # Commentaires
    commentaire = models.TextField(blank=True, help_text="Commentaire de l'enseignant")
    
    # Statut
    is_publie = models.BooleanField(default=True, help_text="Note publiée (visible pour l'étudiant)")
    is_definitive = models.BooleanField(default=False, help_text="Note définitive")
    
    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['-date_publication']
    
    def __str__(self):
        return f"{self.etudiant.matricule} - {self.ue.code} - {self.note_obtenue}/{self.note_maximale}"
    
    def get_pourcentage(self):
        """Calcule le pourcentage de la note"""
        if self.note_maximale > 0:
            return (self.note_obtenue / self.note_maximale) * 100
        return 0
    
    def get_moyenne_ponderee(self):
        """Calcule la moyenne pondérée"""
        return self.note_obtenue * self.coefficient


class InscriptionUE(models.Model):
    """
    Modèle pour l'inscription des étudiants aux UE
    """
    etudiant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inscriptions_ue',
        limit_choices_to={'user_type': 'etudiant'}
    )
    ue = models.ForeignKey(UE, on_delete=models.CASCADE, related_name='inscriptions')
    
    # Dates
    date_inscription = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True, help_text="Date de validation")
    
    # Statut
    is_valide = models.BooleanField(default=False, help_text="Inscription validée")
    is_actif = models.BooleanField(default=True, help_text="Inscription active")
    
    class Meta:
        verbose_name = "Inscription UE"
        verbose_name_plural = "Inscriptions UE"
        unique_together = ['etudiant', 'ue']
        ordering = ['-date_inscription']
    
    def __str__(self):
        return f"{self.etudiant.matricule} - {self.ue.code}"


class Bulletin(models.Model):
    """
    Modèle pour les bulletins de notes
    """
    etudiant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bulletins',
        limit_choices_to={'user_type': 'etudiant'}
    )
    
    # Période
    annee_academique = models.CharField(max_length=9, help_text="Année académique (ex: 2024-2025)")
    semestre = models.CharField(max_length=5, choices=[
        ('S1', 'Semestre 1'), ('S2', 'Semestre 2'),
        ('S3', 'Semestre 3'), ('S4', 'Semestre 4'),
        ('S5', 'Semestre 5'), ('S6', 'Semestre 6'),
        ('S7', 'Semestre 7'), ('S8', 'Semestre 8'),
        ('S9', 'Semestre 9'), ('S10', 'Semestre 10'),
    ])
    
    # Moyennes
    moyenne_semestre = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Moyenne du semestre"
    )
    moyenne_annee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Moyenne de l'année"
    )
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_publication = models.DateTimeField(default=timezone.now, help_text="Date de publication")
    
    # Statut
    is_publie = models.BooleanField(default=True, help_text="Bulletin publié")
    is_definitif = models.BooleanField(default=False, help_text="Bulletin définitif")
    
    class Meta:
        verbose_name = "Bulletin"
        verbose_name_plural = "Bulletins"
        unique_together = ['etudiant', 'annee_academique', 'semestre']
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.etudiant.matricule} - {self.annee_academique} - {self.get_semestre_display()}"
