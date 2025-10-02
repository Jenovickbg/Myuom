#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyUOM.settings')
django.setup()

from users.models import CustomUser

print("👤 Création d'un nouvel administrateur...")

# Créer un superutilisateur administrateur
admin_user = CustomUser.objects.create_superuser(
    username='admin',
    email='admin@uom.cd',
    password='admin123',
    matricule='UOM2025-001',
    first_name='Administrateur',
    last_name='MyUOM',
    user_type='administrateur',
    is_first_login=False
)

print(f"✅ Administrateur créé avec succès!")
print(f"📧 Email: {admin_user.email}")
print(f"🔑 Matricule: {admin_user.matricule}")
print(f"👤 Nom: {admin_user.get_full_name()}")
print(f"🔐 Mot de passe: admin123")
print(f"🌐 URL de connexion: http://127.0.0.1:8000/login/")

print("\n🎉 Tu peux maintenant te connecter avec:")
print("   - Identifiant: admin")
print("   - Mot de passe: admin123")
print("   - Ou avec le matricule: UOM2025-001")
