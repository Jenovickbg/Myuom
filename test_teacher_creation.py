#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyUOM.settings')
django.setup()

from users.models import CustomUser, TeacherProfile
from users.forms import TeacherCreationForm

print("👨‍🏫 Test de création d'un enseignant...")

# Données de test pour l'enseignant
teacher_data = {
    'matricule': 'UOM2025-003',
    'username': 'prof_test',
    'first_name': 'Jean',
    'last_name': 'Professeur',
    'email': 'prof@uom.cd',
    'department': 'Informatique',
    'speciality': 'Réseaux et Télécommunications'
}

# Créer le formulaire
form = TeacherCreationForm(teacher_data)

if form.is_valid():
    print("✅ Formulaire valide")
    try:
        teacher = form.save()
        print(f"✅ Enseignant créé avec succès!")
        print(f"📧 Email: {teacher.email}")
        print(f"🔑 Matricule: {teacher.matricule}")
        print(f"👤 Nom: {teacher.get_full_name()}")
        print(f"🎓 Type: {teacher.user_type}")
        print(f"🔐 Mot de passe: 12345678")
        print(f"🔒 Première connexion: {teacher.is_first_login}")
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
else:
    print("❌ Formulaire invalide")
    for field, errors in form.errors.items():
        for error in errors:
            print(f"  - {field}: {error}")

print("\n🎉 Test terminé!")
