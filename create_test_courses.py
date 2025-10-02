#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyUOM.settings')
django.setup()

from users.models import CustomUser, Faculte, Promotion
from cours.models import Cours

print("🔧 Création des cours de test...")

# Récupérer les données existantes
try:
    # Récupérer une faculté
    faculte = Faculte.objects.first()
    if not faculte:
        print("❌ Aucune faculté trouvée. Créez d'abord des facultés.")
        exit(1)
    
    # Récupérer une promotion
    promotion = Promotion.objects.first()
    if not promotion:
        print("❌ Aucune promotion trouvée. Créez d'abord des promotions.")
        exit(1)
    
    # Récupérer un enseignant
    enseignant = CustomUser.objects.filter(user_type='enseignant').first()
    if not enseignant:
        print("❌ Aucun enseignant trouvé. Créez d'abord des enseignants.")
        exit(1)
    
    # Créer des cours de test
    cours_data = [
        {
            'titre': 'Introduction à la Programmation',
            'code': 'INFO101',
            'description': 'Cours d\'introduction aux concepts de base de la programmation',
            'type_cours': 'cours',
            'niveau': 'L1',
            'filiere': 'Informatique',
            'enseignant': enseignant,
            'faculte': faculte,
            'promotion': promotion,
            'date_debut': date.today(),
            'date_fin': date.today() + timedelta(days=90),
        },
        {
            'titre': 'Travaux Pratiques - Programmation',
            'code': 'INFO101-TP',
            'description': 'Séances de travaux pratiques pour le cours INFO101',
            'type_cours': 'tp',
            'niveau': 'L1',
            'filiere': 'Informatique',
            'enseignant': enseignant,
            'faculte': faculte,
            'promotion': promotion,
            'date_debut': date.today(),
            'date_fin': date.today() + timedelta(days=90),
        },
        {
            'titre': 'Algorithmique et Structures de Données',
            'code': 'INFO201',
            'description': 'Cours avancé sur les algorithmes et structures de données',
            'type_cours': 'cours',
            'niveau': 'L2',
            'filiere': 'Informatique',
            'enseignant': enseignant,
            'faculte': faculte,
            'promotion': promotion,
            'date_debut': date.today(),
            'date_fin': date.today() + timedelta(days=90),
        },
        {
            'titre': 'Projet de Développement Web',
            'code': 'INFO301-PROJET',
            'description': 'Projet de développement d\'une application web',
            'type_cours': 'projet',
            'niveau': 'L3',
            'filiere': 'Informatique',
            'enseignant': enseignant,
            'faculte': faculte,
            'promotion': promotion,
            'date_debut': date.today(),
            'date_fin': date.today() + timedelta(days=120),
        },
    ]
    
    created_count = 0
    for cours_info in cours_data:
        cours, created = Cours.objects.get_or_create(
            code=cours_info['code'],
            defaults=cours_info
        )
        if created:
            created_count += 1
            print(f"✅ Cours créé: {cours.code} - {cours.titre}")
        else:
            print(f"⚠️ Cours déjà existant: {cours.code}")
    
    print(f"🎉 {created_count} cours créés avec succès!")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
