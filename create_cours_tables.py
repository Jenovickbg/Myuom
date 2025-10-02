#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyUOM.settings')
django.setup()

from django.db import connection

print("🔧 Création des tables pour l'app cours...")

with connection.cursor() as cursor:
    # Créer la table cours_cours
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cours_cours (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titre VARCHAR(200) NOT NULL,
            code VARCHAR(20) NOT NULL UNIQUE,
            description TEXT,
            type_cours VARCHAR(20) NOT NULL DEFAULT 'cours',
            niveau VARCHAR(5) NOT NULL,
            filiere VARCHAR(100) NOT NULL,
            enseignant_id INT NOT NULL,
            faculte_id INT,
            promotion_id INT,
            date_creation DATETIME(6) NOT NULL,
            date_debut DATE NOT NULL,
            date_fin DATE NOT NULL,
            is_actif BOOLEAN NOT NULL DEFAULT TRUE,
            is_visible_etudiants BOOLEAN NOT NULL DEFAULT TRUE,
            FOREIGN KEY (enseignant_id) REFERENCES users_customuser(id) ON DELETE CASCADE,
            FOREIGN KEY (faculte_id) REFERENCES users_faculte(id) ON DELETE SET NULL,
            FOREIGN KEY (promotion_id) REFERENCES users_promotion(id) ON DELETE SET NULL
        );
    """)
    
    # Créer la table cours_supportcours
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cours_supportcours (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titre VARCHAR(200) NOT NULL,
            description TEXT,
            type_support VARCHAR(20) NOT NULL DEFAULT 'cours',
            fichier VARCHAR(100) NOT NULL,
            taille_fichier INT,
            cours_id INT NOT NULL,
            enseignant_id INT NOT NULL,
            date_creation DATETIME(6) NOT NULL,
            date_publication DATETIME(6) NOT NULL,
            is_public BOOLEAN NOT NULL DEFAULT TRUE,
            ordre_affichage INT NOT NULL DEFAULT 0,
            FOREIGN KEY (cours_id) REFERENCES cours_cours(id) ON DELETE CASCADE,
            FOREIGN KEY (enseignant_id) REFERENCES users_customuser(id) ON DELETE CASCADE
        );
    """)
    
    # Créer la table cours_inscriptioncours
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cours_inscriptioncours (
            id INT AUTO_INCREMENT PRIMARY KEY,
            etudiant_id INT NOT NULL,
            cours_id INT NOT NULL,
            date_inscription DATETIME(6) NOT NULL,
            date_validation DATETIME(6),
            is_valide BOOLEAN NOT NULL DEFAULT FALSE,
            is_actif BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE KEY unique_inscription (etudiant_id, cours_id),
            FOREIGN KEY (etudiant_id) REFERENCES users_customuser(id) ON DELETE CASCADE,
            FOREIGN KEY (cours_id) REFERENCES cours_cours(id) ON DELETE CASCADE
        );
    """)
    
    print("✅ Tables cours créées avec succès!")

print("🎉 Tables cours créées avec succès!")
