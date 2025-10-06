-- Requêtes SQL CORRIGÉES pour insérer les facultés et promotions
-- Basées sur les vrais champs des modèles Django

-- 1. Insérer les facultés (champs: code, nom, description, is_active, created_at, updated_at)
INSERT INTO users_faculte (code, nom, description, is_active, created_at, updated_at) VALUES
('FSI', 'Faculté des Sciences', 'Sciences exactes et naturelles', 1, NOW(), NOW()),
('FLSH', 'Faculté des Lettres et Sciences Humaines', 'Lettres, langues et sciences humaines', 1, NOW(), NOW()),
('FSEG', 'Faculté des Sciences Économiques et de Gestion', 'Économie, gestion et commerce', 1, NOW(), NOW()),
('FD', 'Faculté de Droit', 'Droit et sciences juridiques', 1, NOW(), NOW()),
('FM', 'Faculté de Médecine', 'Sciences médicales', 1, NOW(), NOW()),
('FI', 'Faculté dIngénierie', 'Ingénierie et technologies', 1, NOW(), NOW());

-- 2. Insérer les promotions (champs: annee_debut, annee_fin, is_active, created_at, updated_at)
INSERT INTO users_promotion (annee_debut, annee_fin, is_active, created_at, updated_at) VALUES
(2020, 2021, 1, NOW(), NOW()),
(2021, 2022, 1, NOW(), NOW()),
(2022, 2023, 1, NOW(), NOW()),
(2023, 2024, 1, NOW(), NOW()),
(2024, 2025, 1, NOW(), NOW()),
(2025, 2026, 1, NOW(), NOW());

-- 3. Vérifier l'insertion
SELECT 'FACULTÉS CRÉÉES:' as info;
SELECT id, code, nom, description FROM users_faculte ORDER BY id;

SELECT 'PROMOTIONS CRÉÉES:' as info;
SELECT id, annee_debut, annee_fin FROM users_promotion ORDER BY id;
