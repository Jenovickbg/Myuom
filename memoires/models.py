from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import random

User = get_user_model()


class Memoire(models.Model):
    """
    Modèle pour les mémoires de fin d'études (L3 et M2)
    """
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('soumis', 'Soumis pour validation'),
        ('valide', 'Validé'),
        ('refuse', 'Refusé'),
        ('en_cours', 'En cours de rédaction'),
        ('termine', 'Terminé'),
        ('certifie', 'Certifié'),
    ]
    
    DOMAINE_CHOICES = [
        ('informatique', 'Informatique'),
        ('genie_civil', 'Génie Civil'),
        ('gestion', 'Gestion'),
        ('droit', 'Droit'),
        ('sciences', 'Sciences'),
        ('lettres', 'Lettres'),
        ('economie', 'Économie'),
        ('autre', 'Autre'),
    ]
    
    # Étudiant
    etudiant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memoires_etudiant',
        limit_choices_to={'user_type': 'etudiant'}
    )
    
    # Informations du sujet
    titre = models.CharField(max_length=500, help_text="Titre du mémoire")
    description = models.TextField(help_text="Description détaillée du sujet")
    objectifs = models.TextField(help_text="Objectifs du mémoire")
    domaine = models.CharField(max_length=50, choices=DOMAINE_CHOICES, help_text="Domaine d'étude")
    domaine_autre = models.CharField(max_length=200, blank=True, null=True, help_text="Précisez si 'Autre'")
    
    # Encadrement
    directeur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='memoires_directeur',
        limit_choices_to={'user_type': 'enseignant'},
        help_text="Directeur du mémoire"
    )
    encadreur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='memoires_encadreur',
        limit_choices_to={'user_type': 'enseignant'},
        help_text="Encadreur du mémoire"
    )
    
    # Fichier du mémoire final
    fichier_memoire = models.FileField(
        upload_to='memoires/documents/%Y/%m/',
        blank=True,
        null=True,
        help_text="Fichier PDF du mémoire final"
    )
    
    # Dates
    date_soumission_sujet = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    date_depot_final = models.DateTimeField(null=True, blank=True)
    date_certification = models.DateTimeField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    
    # Commentaires
    commentaire_etudiant = models.TextField(blank=True, help_text="Commentaire de l'étudiant")
    commentaire_admin = models.TextField(blank=True, help_text="Commentaire de l'administration")
    motif_refus = models.TextField(blank=True, help_text="Motif de refus du sujet")
    
    # Anti-plagiat
    score_plagiat = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score de plagiat (0-100%)"
    )
    rapport_plagiat = models.TextField(blank=True, help_text="Rapport anti-plagiat")
    plagiat_verifie = models.BooleanField(default=False)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Mémoire"
        verbose_name_plural = "Mémoires"
        ordering = ['-date_soumission_sujet']
    
    def __str__(self):
        return f"{self.etudiant.get_full_name()} - {self.titre[:50]}"
    
    def get_niveau_etudiant(self):
        """Retourne le niveau de l'étudiant"""
        try:
            return self.etudiant.student_profile.niveau
        except:
            return None
    
    def peut_deposer_final(self):
        """Vérifie si l'étudiant peut déposer le mémoire final"""
        return self.statut == 'valide' or self.statut == 'en_cours'
    
    def lancer_verification_plagiat(self):
        """Simule une vérification anti-plagiat"""
        # Simulation : score aléatoire entre 5% et 25%
        self.score_plagiat = random.uniform(5.0, 25.0)
        self.plagiat_verifie = True
        
        # Générer un rapport simulé
        self.rapport_plagiat = f"""
=== RAPPORT D'ANALYSE ANTI-PLAGIAT ===
Document: {self.titre}
Étudiant: {self.etudiant.get_full_name()}
Date d'analyse: {timezone.now().strftime('%d/%m/%Y %H:%M')}

Score de similarité: {self.score_plagiat:.2f}%

Analyse détaillée:
- Sources internet: {random.uniform(2, 10):.1f}%
- Publications académiques: {random.uniform(1, 8):.1f}%
- Travaux étudiants: {random.uniform(1, 5):.1f}%
- Autres sources: {random.uniform(1, 7):.1f}%

Évaluation: {"ACCEPTABLE" if self.score_plagiat < 20 else "À VÉRIFIER"}

Note: Ce rapport est une simulation pour démonstration.
        """
        self.save()
        
        return self.score_plagiat < 20  # Seuil d'acceptation: 20%


class CertificatMemoire(models.Model):
    """
    Certificat de dépôt de mémoire
    """
    memoire = models.OneToOneField(Memoire, on_delete=models.CASCADE, related_name='certificat')
    numero_certificat = models.CharField(max_length=50, unique=True)
    date_emission = models.DateTimeField(auto_now_add=True)
    
    # Informations du certificat
    annee_academique = models.CharField(max_length=9, help_text="Année académique (ex: 2024-2025)")
    
    class Meta:
        verbose_name = "Certificat de Mémoire"
        verbose_name_plural = "Certificats de Mémoire"
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"Certificat {self.numero_certificat} - {self.memoire.etudiant.get_full_name()}"
    
    @staticmethod
    def generer_numero():
        """Génère un numéro de certificat unique"""
        import uuid
        annee = timezone.now().year
        code = str(uuid.uuid4())[:8].upper()
        return f"CERT-MEM-{annee}-{code}"



