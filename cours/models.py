from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Cours(models.Model):
    """
    Modèle pour les cours
    """
    TYPE_COURS_CHOICES = [
        ('cours', 'Cours Magistral'),
        ('tp', 'Travaux Pratiques'),
        ('td', 'Travaux Dirigés'),
        ('projet', 'Projet'),
    ]
    
    NIVEAU_CHOICES = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
    ]
    
    # Informations de base
    titre = models.CharField(max_length=200, help_text="Titre du cours")
    code = models.CharField(max_length=20, unique=True, help_text="Code du cours (ex: INFO101)")
    description = models.TextField(blank=True, help_text="Description du cours")
    
    # Classification
    type_cours = models.CharField(max_length=20, choices=TYPE_COURS_CHOICES, default='cours')
    niveau = models.CharField(max_length=5, choices=NIVEAU_CHOICES)
    filiere = models.CharField(max_length=100, help_text="Filière concernée")
    credits = models.PositiveIntegerField(default=3, help_text="Nombre de crédits ECTS")
    
    # Enseignant responsable
    enseignant = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='cours_enseignant',
        limit_choices_to={'user_type': 'enseignant'}
    )
    
    # Faculté et promotion
    faculte = models.ForeignKey(
        'users.Faculte',
        on_delete=models.CASCADE,
        related_name='cours_faculte',
        help_text="Faculté du cours",
        null=True,
        blank=True
    )
    
    promotion = models.ForeignKey(
        'users.Promotion',
        on_delete=models.CASCADE,
        related_name='cours_promotion',
        help_text="Promotion concernée",
        null=True,
        blank=True
    )
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateField(help_text="Date de début du cours")
    date_fin = models.DateField(help_text="Date de fin du cours")
    
    # Statut
    is_actif = models.BooleanField(default=True, help_text="Cours actif")
    is_visible_etudiants = models.BooleanField(default=True, help_text="Visible pour les étudiants")
    
    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.code} - {self.titre}"
    
    def get_display_name(self):
        return f"{self.code} - {self.titre}"


class SupportCours(models.Model):
    """
    Modèle pour les supports de cours (documents, fichiers)
    """
    TYPE_SUPPORT_CHOICES = [
        ('cours', 'Support de cours'),
        ('tp', 'TP'),
        ('td', 'TD'),
        ('corrige', 'Corrigé'),
        ('autre', 'Autre'),
    ]
    
    # Informations de base
    titre = models.CharField(max_length=200, help_text="Titre du support")
    description = models.TextField(blank=True, help_text="Description du support")
    type_support = models.CharField(max_length=20, choices=TYPE_SUPPORT_CHOICES, default='cours')
    
    # Fichier
    fichier = models.FileField(
        upload_to='cours/supports/%Y/%m/',
        help_text="Fichier du support"
    )
    taille_fichier = models.PositiveIntegerField(null=True, blank=True, help_text="Taille en octets")
    
    # Relations
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='supports')
    enseignant = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='supports_enseignant',
        limit_choices_to={'user_type': 'enseignant'}
    )
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_publication = models.DateTimeField(default=timezone.now, help_text="Date de publication")
    
    # Visibilité
    is_public = models.BooleanField(default=True, help_text="Visible pour les étudiants")
    ordre_affichage = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    
    class Meta:
        verbose_name = "Support de cours"
        verbose_name_plural = "Supports de cours"
        ordering = ['ordre_affichage', '-date_publication']
    
    def __str__(self):
        return f"{self.cours.code} - {self.titre}"
    
    def save(self, *args, **kwargs):
        # Calculer la taille du fichier
        if self.fichier:
            self.taille_fichier = self.fichier.size
        super().save(*args, **kwargs)


class InscriptionCours(models.Model):
    """
    Modèle pour l'inscription des étudiants aux cours
    """
    etudiant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inscriptions_cours',
        limit_choices_to={'user_type': 'etudiant'}
    )
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='inscriptions')
    
    # Dates
    date_inscription = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True, help_text="Date de validation par l'enseignant")
    
    # Statut
    is_valide = models.BooleanField(default=False, help_text="Inscription validée")
    is_actif = models.BooleanField(default=True, help_text="Inscription active")
    
    class Meta:
        verbose_name = "Inscription au cours"
        verbose_name_plural = "Inscriptions aux cours"
        unique_together = ['etudiant', 'cours']
        ordering = ['-date_inscription']
    
    def __str__(self):
        return f"{self.etudiant.matricule} - {self.cours.code}"
