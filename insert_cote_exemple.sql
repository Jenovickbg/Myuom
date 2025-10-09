-- Exemple d'insertion de cote pour un étudiant
-- Remplacez les valeurs selon vos besoins

-- 1. Trouver l'ID de l'étudiant
-- SELECT id, matricule, first_name, last_name FROM users_customuser WHERE user_type='etudiant';

-- 2. Insérer la cote
INSERT INTO resultats_coteetudiant (
    etudiant_id,
    annee_academique,
    semestre,
    moyenne,
    total_credits,
    total_credits_possible,
    mention,
    decision,
    nombre_ue_a_reprendre,
    observation,
    date_creation,
    date_modification,
    cree_par_id,
    is_definitif
) VALUES (
    2,                      -- ID de l'étudiant (remplacer par l'ID réel)
    '2024-2025',           -- Année académique
    'S1',                  -- Semestre (S1, S2, etc.)
    14.75,                 -- Moyenne obtenue
    30,                    -- Total crédits obtenus
    30,                    -- Total crédits possibles
    'bien',                -- Mention: excellent, tres_bien, bien, assez_bien, passable, mediocre, faible, tres_faible
    'admis',               -- Décision: admis, ajourne, repechage, exclus
    0,                     -- Nombre d'UE à reprendre
    'Bon travail! Continue ainsi.',  -- Observation
    NOW(),                 -- Date de création
    NOW(),                 -- Date de modification
    NULL,                  -- ID du créateur (optionnel)
    1                      -- 1 = définitif, 0 = provisoire
);

-- 3. Vérifier l'insertion
-- SELECT * FROM resultats_coteetudiant WHERE etudiant_id = 2;

-- 4. Mettre à jour une cote existante
/*
UPDATE resultats_coteetudiant 
SET moyenne = 15.50,
    total_credits = 30,
    mention = 'bien',
    decision = 'admis',
    nombre_ue_a_reprendre = 0,
    observation = 'Excellent travail!',
    date_modification = NOW(),
    is_definitif = 1
WHERE etudiant_id = 2 
  AND annee_academique = '2024-2025' 
  AND semestre = 'S1';
*/

-- GUIDE DES MENTIONS (selon la moyenne):
-- >= 18  : excellent
-- >= 16  : tres_bien
-- >= 14  : bien
-- >= 12  : assez_bien
-- >= 10  : passable
-- >= 8   : mediocre
-- >= 6   : faible
-- < 6    : tres_faible

-- GUIDE DES DÉCISIONS:
-- Moyenne >= 10 ET nombre_ue_a_reprendre = 0  : admis
-- Moyenne >= 8  ET nombre_ue_a_reprendre <= 2 : repechage
-- Sinon                                        : ajourne

