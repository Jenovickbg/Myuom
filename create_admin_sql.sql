-- Script SQL pour créer un administrateur MyUOM
-- Base de données: myuom

-- 1. Créer l'utilisateur administrateur
INSERT INTO users_customuser (
    username, 
    email, 
    first_name, 
    last_name, 
    matricule, 
    user_type, 
    is_active, 
    is_staff, 
    is_superuser, 
    date_joined, 
    password
) VALUES (
    'admin', 
    'admin@uom.cd', 
    'Administrateur', 
    'MyUOM', 
    'ADMIN001', 
    'admin', 
    1, 
    1, 
    1, 
    NOW(), 
     'pbkdf2_sha256$216000$EUnsgiqSai96$CVxftkZL9/TIj1So2Jh0+h5fG4E7yqrmyFvNPmqlNJg='  -- Mot de passe: 12345678
);

-- 2. Récupérer l'ID de l'administrateur créé
SET @admin_id = LAST_INSERT_ID();

-- 3. Créer le profil administrateur (optionnel, pour la cohérence)
INSERT INTO users_adminprofile (
    user_id,
    telephone,
    adresse,
    created_at,
    updated_at
) VALUES (
    @admin_id,
    '+243123456789',
    'Université de Mbujimayi',
    NOW(),
    NOW()
);
                         
-- 5. Informations de connexion
SELECT 
    '=== INFORMATIONS DE CONNEXION ADMIN ===' as info,
    'Username: admin' as username,
    'Matricule: ADMIN001' as matricule,
    'Mot de passe: 12345678' as password,
    'URL: http://127.0.0.1:8000/login/' as url;
