from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


class Faculte(models.Model):
    """Modèle pour gérer les facultés"""
    code = models.CharField(max_length=10, unique=True, help_text="Code de la faculté (ex: FSI)")
    nom = models.CharField(max_length=100, help_text="Nom complet de la faculté")
    description = models.TextField(blank=True, help_text="Description de la faculté")
    is_active = models.BooleanField(default=True, help_text="Faculté active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Faculté"
        verbose_name_plural = "Facultés"
        ordering = ['nom']

    def __str__(self):
        return f"{self.code} - {self.nom}"


class Promotion(models.Model):
    """Modèle pour gérer les promotions"""
    annee_debut = models.IntegerField(help_text="Année de début (ex: 2023)")
    annee_fin = models.IntegerField(help_text="Année de fin (ex: 2024)")
    is_active = models.BooleanField(default=True, help_text="Promotion active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"
        ordering = ['-annee_debut']
        unique_together = ['annee_debut', 'annee_fin']

    def __str__(self):
        return f"{self.annee_debut}-{self.annee_fin}"

    @property
    def nom_complet(self):
        return f"{self.annee_debut}-{self.annee_fin}"


class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé pour MyUOM
    Gère les étudiants, enseignants et administrateurs
    """
    
    # Types d'utilisateurs
    USER_TYPE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('admin', 'Administrateur'),
    ]
    
    # Validateur pour le matricule (format: UOM2025-001)
    matricule_validator = RegexValidator(
        regex=r'^UOM\d{4}-\d{3}$',
        message='Le matricule doit être au format UOM2025-001'
    )
    
    # Champs personnalisés
    matricule = models.CharField(
        max_length=15,
        unique=True,
        validators=[matricule_validator],
        help_text="Matricule unique (ex: UOM2025-001)"
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='etudiant',
        help_text="Type d'utilisateur"
    )
    
    # Informations personnelles
    birth_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date de naissance"
    )
    
    birth_place = models.CharField(
        max_length=100,
        blank=True,
        help_text="Lieu de naissance"
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Numéro de téléphone"
    )
    
    # Gestion de la première connexion
    is_first_login = models.BooleanField(
        default=True,
        help_text="Première connexion (doit changer le mot de passe)"
    )
    
    # Statut du compte
    is_active_student = models.BooleanField(
        default=False,
        help_text="Compte étudiant activé (après première connexion)"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['matricule']
    
    def __str__(self):
        return f"{self.matricule} - {self.get_full_name() or self.username}"
    
    def get_display_name(self):
        """Retourne le nom d'affichage complet"""
        if self.get_full_name():
            return f"{self.get_full_name()} ({self.matricule})"
        return f"{self.username} ({self.matricule})"
    
    def is_student(self):
        """Vérifie si l'utilisateur est un étudiant"""
        return self.user_type == 'etudiant'
    
    def is_teacher(self):
        """Vérifie si l'utilisateur est un enseignant"""
        return self.user_type == 'enseignant'
    
    def is_admin_user(self):
        """Vérifie si l'utilisateur est un administrateur"""
        return self.user_type == 'admin'
    
    def is_student_user(self):
        """Vérifie si l'utilisateur est un étudiant (alias pour compatibilité)"""
        return self.user_type == 'etudiant'
    
    def is_teacher_user(self):
        """Vérifie si l'utilisateur est un enseignant (alias pour compatibilité)"""
        return self.user_type == 'enseignant'
    
    def needs_password_change(self):
        """Vérifie si l'utilisateur doit changer son mot de passe"""
        return self.is_first_login
    
    def complete_first_login(self):
        """Marque la première connexion comme terminée"""
        self.is_first_login = False
        if self.is_student():
            self.is_active_student = True
        self.save()


class StudentProfile(models.Model):
    """
    Profil étendu pour les étudiants
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    
    # Photo de profil
    photo = models.ImageField(
        upload_to='profiles/students/%Y/%m/',
        blank=True,
        null=True,
        help_text="Photo de profil"
    )

    # Informations académiques
    niveau = models.CharField(
        max_length=20,
        choices=[
            ('L1', 'Licence 1'),
            ('L2', 'Licence 2'),
            ('L3', 'Licence 3'),
            ('M1', 'Master 1'),
            ('M2', 'Master 2'),
        ],
        blank=True
    )
    
    filiere = models.CharField(
        max_length=100,
        blank=True,
        help_text="Filière d'étude"
    )
    
    # Faculté et promotion (relations)
    faculte = models.ForeignKey(
        Faculte,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Faculté d'appartenance"
    )
    
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Promotion d'appartenance"
    )
    
    # Informations de contact d'urgence
    emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        help_text="Contact d'urgence"
    )
    
    emergency_phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Téléphone d'urgence"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil Étudiant"
        verbose_name_plural = "Profils Étudiants"
    
    def __str__(self):
        return f"Profil de {self.user.get_display_name()}"

    def save(self, *args, **kwargs):
        """
        Sauvegarde du profil avec post-traitement de la photo:
        - recadrage centre en carré
        - redimensionnement doux à 256x256
        """
        super().save(*args, **kwargs)

        if self.photo and self.photo.name:
            try:
                from PIL import Image
                import os
                from django.conf import settings

                photo_path = self.photo.path
                with Image.open(photo_path) as img:
                    img = img.convert('RGB')
                    width, height = img.size
                    # recadrage centre carré
                    min_edge = min(width, height)
                    left = (width - min_edge) // 2
                    top = (height - min_edge) // 2
                    right = left + min_edge
                    bottom = top + min_edge
                    img = img.crop((left, top, right, bottom))

                    # redimensionner à 256x256
                    img = img.resize((256, 256), Image.LANCZOS)

                    # réécrire le fichier (JPEG)
                    img.save(photo_path, format='JPEG', quality=90)
            except Exception:
                # En cas de problème d'image, on ne bloque pas la sauvegarde
                pass


class TeacherProfile(models.Model):
    """
    Profil étendu pour les enseignants
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    
    # Informations professionnelles
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Département"
    )
    
    speciality = models.CharField(
        max_length=100,
        blank=True,
        help_text="Spécialité"
    )
    
    office = models.CharField(
        max_length=50,
        blank=True,
        help_text="Bureau"
    )
    
    # Faculté d'appartenance
    faculte = models.ForeignKey(
        Faculte,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Faculté d'appartenance"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil Enseignant"
        verbose_name_plural = "Profils Enseignants"
    
    def __str__(self):
        return f"Profil de {self.user.get_display_name()}"
