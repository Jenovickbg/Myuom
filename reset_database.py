#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyUOM.settings')
django.setup()

from users.models import CustomUser, StudentProfile, TeacherProfile, Faculte, Promotion

print("🗑️ Suppression des données existantes...")

# Supprimer tous les profils étudiants et enseignants
StudentProfile.objects.all().delete()
TeacherProfile.objects.all().delete()
print("✅ Profils étudiants et enseignants supprimés")

# Supprimer tous les utilisateurs (sauf les superusers)
CustomUser.objects.filter(is_superuser=False).delete()
print("✅ Utilisateurs supprimés (sauf superusers)")

# Supprimer les facultés et promotions existantes
Faculte.objects.all().delete()
Promotion.objects.all().delete()
print("✅ Facultés et promotions supprimées")

print("\n🏛️ Création des facultés...")
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
