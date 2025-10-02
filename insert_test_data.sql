-- ============================================
-- REQUÊTES SQL POUR INSÉRER DES DONNÉES DE TEST
-- ============================================

-- 1. INSÉRER UN ENSEIGNANT
INSERT INTO users_customuser (
    username, matricule, user_type, first_name, last_name, 
    email, password, is_staff, is_superuser, is_active, is_first_login,
    date_joined, created_at, updated_at
) VALUES (
    'prof_test', 'UOM2025-E002', 'enseignant', 'Jean', 'Dupont',
    'jean.dupont@uom.cd', 'pbkdf2_sha256$216000$Jc9m8KZms17f$FX71euwKhWUzbhVxHbbZJKHMYXqcCsoVUcVDyN/2KHY=', 0, 0, 1, 0,
    NOW(), NOW(), NOW()
);

-- Récupérer l'ID de l'enseignant créé
SET @teacher_id = LAST_INSERT_ID();

-- Créer le profil enseignant
INSERT INTO users_teacherprofile (
    user_id, department, speciality, office, created_at, updated_at
) VALUES (
    @teacher_id, 'Informatique', 'Développement Web', 'Bureau A-101', NOW(), NOW()
);

-- 2. INSÉRER UN ÉTUDIANT
INSERT INTO users_customuser (
    username, matricule, user_type, first_name, last_name, 
    email, password, is_staff, is_superuser, is_active, is_first_login,
    date_joined, created_at, updated_at
) VALUES (
    'etudiant_test', 'UOM2025-103', 'etudiant', 'Marie', 'Martin',
    'marie.martin@uom.cd', 'pbkdf2_sha256$216000$GCXmpsueuBrq$0kZpzlNdE4dt6wU6jHpgJDx6ISOYQyGPgVdiy4jgeqQ=', 0, 0, 1, 0,
    NOW(), NOW(), NOW()
);

-- Récupérer l'ID de l'étudiant créé
SET @student_id = LAST_INSERT_ID();

-- Créer le profil étudiant
INSERT INTO users_studentprofile (
    user_id, niveau, filiere, emergency_contact, emergency_phone,
    created_at, updated_at
) VALUES (
    @student_id, 'L2', 'Informatique', 'Papa Martin', '+243 123 456 789',
    NOW(), NOW()
);

-- 3. INSÉRER UN COURS
INSERT INTO cours_cours (
    titre, code, description, type_cours, niveau, filiere,
    enseignant_id, date_creation, date_debut, date_fin,
    is_actif, is_visible_etudiants, created_at, updated_at
) VALUES (
    'Développement Web', 'INF-L2-001', 'Cours de développement web avec HTML, CSS, JavaScript',
    'cours', 'L2', 'Informatique',
    @teacher_id, NOW(), '2025-01-15', '2025-06-15',
    1, 1, NOW(), NOW()
);

-- Récupérer l'ID du cours créé
SET @course_id = LAST_INSERT_ID();

-- 4. INSCRIRE L'ÉTUDIANT AU COURS
INSERT INTO cours_inscriptioncours (
    etudiant_id, cours_id, date_inscription, is_actif, created_at, updated_at
) VALUES (
    @student_id, @course_id, NOW(), 1, NOW(), NOW()
);

-- 5. INSÉRER UN SUPPORT DE COURS
INSERT INTO cours_supportcours (
    titre, description, type_support, cours_id, enseignant_id,
    date_creation, date_publication, is_public, ordre_affichage,
    created_at, updated_at
) VALUES (
    'Introduction au HTML', 'Support de cours sur les bases du HTML',
    'cours', @course_id, @teacher_id,
    NOW(), NOW(), 1, 1,
    NOW(), NOW()
);

-- 6. INSÉRER UN TRAVAIL (TP/TD)
INSERT INTO travaux_travail (
    titre, description, consignes, type_travail, niveau, filiere,
    enseignant_id, date_creation, date_publication, date_limite_remise,
    date_limite_correction, note_maximale, coefficient, statut,
    is_visible_etudiants, created_at, updated_at
) VALUES (
    'TP1 - Site Web Personnel', 'Créer un site web personnel avec HTML/CSS',
    'Créer un site web de 3 pages minimum avec navigation',
    'tp', 'L2', 'Informatique',
    @teacher_id, NOW(), NOW(), DATE_ADD(NOW(), INTERVAL 14 DAY),
    DATE_ADD(NOW(), INTERVAL 21 DAY), 20, 1.0, 'publie',
    1, NOW(), NOW()
);

-- Récupérer l'ID du travail créé
SET @travail_id = LAST_INSERT_ID();

-- 7. INSÉRER UNE UE (Unité d'Enseignement)
INSERT INTO resultats_ue (
    code, nom, description, niveau, semestre, filiere,
    credits, coefficient, enseignant_responsable_id,
    date_creation, date_debut, date_fin, is_actif,
    is_visible_etudiants, created_at, updated_at
) VALUES (
    'UE-INF-L2-001', 'Développement Web', 'Unité d\'enseignement développement web',
    'L2', 'S1', 'Informatique', 6, 1.0, @teacher_id,
    NOW(), '2025-01-15', '2025-06-15', 1, 1, NOW(), NOW()
);

-- Récupérer l'ID de l'UE créée
SET @ue_id = LAST_INSERT_ID();

-- 8. INSCRIRE L'ÉTUDIANT À L'UE
INSERT INTO resultats_inscriptionue (
    etudiant_id, ue_id, date_inscription, is_actif, created_at, updated_at
) VALUES (
    @student_id, @ue_id, NOW(), 1, NOW(), NOW()
);

-- 9. INSÉRER UNE NOTE
INSERT INTO resultats_note (
    etudiant_id, ue_id, type_note, titre, description,
    note_obtenue, note_maximale, coefficient, enseignant_id,
    date_evaluation, date_publication, commentaire, is_publie,
    is_definitive, created_at, updated_at
) VALUES (
    @student_id, @ue_id, 'controle', 'Contrôle HTML/CSS', 'Évaluation des connaissances HTML/CSS',
    15, 20, 0.4, @teacher_id,
    NOW(), NOW(), 'Bon travail, continuez ainsi !', 1, 1, NOW(), NOW()
);

-- ============================================
-- VÉRIFICATION DES DONNÉES INSÉRÉES
-- ============================================

-- Vérifier l'enseignant
SELECT 'ENSEIGNANT CRÉÉ:' as info;
SELECT u.username, u.matricule, u.first_name, u.last_name, t.department, t.speciality
FROM users_customuser u
JOIN users_teacherprofile t ON u.id = t.user_id
WHERE u.matricule = 'UOM2025-E002';

-- Vérifier l'étudiant
SELECT 'ÉTUDIANT CRÉÉ:' as info;
SELECT u.username, u.matricule, u.first_name, u.last_name, s.niveau, s.filiere
FROM users_customuser u
JOIN users_studentprofile s ON u.id = s.user_id
WHERE u.matricule = 'UOM2025-103';

-- Vérifier le cours
SELECT 'COURS CRÉÉ:' as info;
SELECT c.titre, c.code, c.niveau, u.first_name, u.last_name
FROM cours_cours c
JOIN users_customuser u ON c.enseignant_id = u.id
WHERE c.code = 'INF-L2-001';

-- Vérifier l'inscription
SELECT 'INSCRIPTION ÉTUDIANT:' as info;
SELECT c.titre, u.first_name, u.last_name, i.date_inscription
FROM cours_inscriptioncours i
JOIN cours_cours c ON i.cours_id = c.id
JOIN users_customuser u ON i.etudiant_id = u.id
WHERE u.matricule = 'UOM2025-103';

-- Vérifier le travail
SELECT 'TRAVAIL CRÉÉ:' as info;
SELECT t.titre, t.type_travail, t.niveau, u.first_name, u.last_name
FROM travaux_travail t
JOIN users_customuser u ON t.enseignant_id = u.id
WHERE t.titre LIKE '%Site Web Personnel%';

-- Vérifier l'UE et la note
SELECT 'UE ET NOTE:' as info;
SELECT ue.nom, n.titre, n.note_obtenue, n.note_maximale, n.commentaire
FROM resultats_ue ue
JOIN resultats_note n ON ue.id = n.ue_id
JOIN users_customuser etu ON n.etudiant_id = etu.id
WHERE etu.matricule = 'UOM2025-103';
