#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyUOM.settings')
django.setup()

from django.db import connection

print("🗑️ Réinitialisation complète de la base de données...")

# Utiliser des commandes SQL directes
with connection.cursor() as cursor:
    # Supprimer les tables dans l'ordre correct
    print("Suppression des tables...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    # Supprimer les tables users
    cursor.execute("DROP TABLE IF EXISTS users_studentprofile;")
    cursor.execute("DROP TABLE IF EXISTS users_teacherprofile;")
    cursor.execute("DROP TABLE IF EXISTS users_customuser;")
    cursor.execute("DROP TABLE IF EXISTS users_faculte;")
    cursor.execute("DROP TABLE IF EXISTS users_promotion;")
    
    # Supprimer les autres tables
    cursor.execute("DROP TABLE IF EXISTS cours_inscriptioncours;")
    cursor.execute("DROP TABLE IF EXISTS cours_supportcours;")
    cursor.execute("DROP TABLE IF EXISTS cours_cours;")
    cursor.execute("DROP TABLE IF EXISTS travaux_remisetravail;")
    cursor.execute("DROP TABLE IF EXISTS travaux_travail;")
    cursor.execute("DROP TABLE IF EXISTS resultats_inscriptionue;")
    cursor.execute("DROP TABLE IF EXISTS resultats_note;")
    cursor.execute("DROP TABLE IF EXISTS resultats_bulletin;")
    cursor.execute("DROP TABLE IF EXISTS resultats_ue;")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    print("✅ Tables supprimées")

print("🔄 Application des migrations...")
os.system("python manage.py migrate")

print("🏛️ Création des facultés...")
from users.models import Faculte, Promotion

facultes = [
    ('FSI', 'Faculté des Sciences de l\'Ingénieur', 'Formation en ingénierie et technologies'),
    ('FSEG', 'Faculté des Sciences Économiques et de Gestion', 'Formation en économie et gestion'),
    ('FAS', 'Faculté des Arts et Sciences', 'Formation en arts et sciences humaines'),
    ('FDS', 'Faculté de Droit et Sciences Politiques', 'Formation en droit et sciences politiques'),
    ('FMS', 'Faculté de Médecine et Sciences de la Santé', 'Formation en médecine et sciences de la santé'),
]

for code, nom, desc in facultes:
    faculte = Faculte.objects.create(code=code, nom=nom, description=desc)
    print(f"✅ {code} - {nom}")

print("\n📅 Création des promotions...")
promotions = [
    (2020, 2021),
    (2021, 2022),
    (2022, 2023),
    (2023, 2024),
    (2024, 2025),
    (2025, 2026),
]

for debut, fin in promotions:
    promotion = Promotion.objects.create(annee_debut=debut, annee_fin=fin)
    print(f"✅ {debut}-{fin}")

print("\n🎉 Base de données réinitialisée avec succès!")
print("📝 Tu peux maintenant créer des étudiants avec les nouvelles facultés et promotions.")
