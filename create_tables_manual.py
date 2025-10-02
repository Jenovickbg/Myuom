#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyUOM.settings')
django.setup()

from django.db import connection

print("🔧 Création manuelle des tables...")

with connection.cursor() as cursor:
    # Créer la table users_faculte
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_faculte (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(10) NOT NULL UNIQUE,
            nom VARCHAR(100) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME(6) NOT NULL,
            updated_at DATETIME(6) NOT NULL
        );
    """)
    
    # Créer la table users_promotion
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_promotion (
            id INT AUTO_INCREMENT PRIMARY KEY,
            annee_debut INT NOT NULL,
            annee_fin INT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME(6) NOT NULL,
            updated_at DATETIME(6) NOT NULL,
            UNIQUE KEY unique_promotion_years (annee_debut, annee_fin)
        );
    """)
    
    # Créer la table users_customuser
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_customuser (
            id INT AUTO_INCREMENT PRIMARY KEY,
            password VARCHAR(128) NOT NULL,
            last_login DATETIME(6),
            is_superuser BOOLEAN NOT NULL,
            username VARCHAR(150) NOT NULL UNIQUE,
            first_name VARCHAR(150) NOT NULL,
            last_name VARCHAR(150) NOT NULL,
            email VARCHAR(254),
            is_staff BOOLEAN NOT NULL,
            is_active BOOLEAN NOT NULL,
            date_joined DATETIME(6) NOT NULL,
            matricule VARCHAR(15) NOT NULL UNIQUE,
            user_type VARCHAR(20) NOT NULL,
            birth_date DATE,
            birth_place VARCHAR(100),
            phone VARCHAR(15),
            is_first_login BOOLEAN NOT NULL,
            is_active_student BOOLEAN NOT NULL,
            created_at DATETIME(6) NOT NULL,
            updated_at DATETIME(6) NOT NULL
        );
    """)
    
    # Créer la table users_studentprofile
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_studentprofile (
            id INT AUTO_INCREMENT PRIMARY KEY,
            photo VARCHAR(100),
            niveau VARCHAR(20),
            filiere VARCHAR(100),
            faculte_id INT,
            promotion_id INT,
            emergency_contact VARCHAR(100),
            emergency_phone VARCHAR(15),
            created_at DATETIME(6) NOT NULL,
            updated_at DATETIME(6) NOT NULL,
            user_id INT NOT NULL UNIQUE,
            FOREIGN KEY (user_id) REFERENCES users_customuser(id) ON DELETE CASCADE,
            FOREIGN KEY (faculte_id) REFERENCES users_faculte(id) ON DELETE SET NULL,
            FOREIGN KEY (promotion_id) REFERENCES users_promotion(id) ON DELETE SET NULL
        );
    """)
    
    # Créer la table users_teacherprofile
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_teacherprofile (
            id INT AUTO_INCREMENT PRIMARY KEY,
            department VARCHAR(100),
            speciality VARCHAR(100),
            office VARCHAR(100),
            created_at DATETIME(6) NOT NULL,
            updated_at DATETIME(6) NOT NULL,
            user_id INT NOT NULL UNIQUE,
            FOREIGN KEY (user_id) REFERENCES users_customuser(id) ON DELETE CASCADE
        );
    """)
    
    print("✅ Tables créées avec succès!")

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
