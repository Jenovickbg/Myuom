-- Script SQL CORRIGÉ pour créer des administrateurs MyUOM
-- Base de données: myuom
-- Hash Django générés avec make_password()

-- 1. Créer l'administrateur principal
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
    'pbkdf2_sha256$216000$EUnsgiqSai96$CVxftkZL9/TIj1So2Jh0+h5fG4E7yqrmyFvNPmqlNJg='
);

-- 2. Créer un super administrateur
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
    'superadmin', 
    'superadmin@uom.cd', 
    'Super', 
    'Administrateur', 
    'SUPER001', 
    'admin', 
    1, 
    1, 
    1, 
    NOW(), 
    'pbkdf2_sha256$216000$uKAGQt8dOWTM$XVGULJfPYIMdmmslCQ/IlAmkj3qFbrk3oDkNnFG8xj0='
);

-- 3. Créer un directeur
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
    'directeur', 
    'directeur@uom.cd', 
    'Directeur', 
    'Général', 
    'DIR001', 
    'admin', 
    1, 
    1, 
    1, 
    NOW(), 
    'pbkdf2_sha256$216000$WP1zeSvKjop5$21Q3sSQABnzeC/iuVtZmxHFTAFHIH6G6BD6OAKAzaKQ='
);

-- 4. Vérifier la création des administrateurs
SELECT 
    id,
    username,
    first_name,
    last_name,
    matricule,
    user_type,
    is_active,
    is_staff,
    is_superuser,
    date_joined
FROM users_customuser 
WHERE user_type = 'admin'
ORDER BY date_joined;

-- 5. Informations de connexion
SELECT 
    '=== INFORMATIONS DE CONNEXION ADMINISTRATEURS ===' as info,
    '' as separator,
    'ADMINISTRATEUR PRINCIPAL:' as admin1,
    'Username: admin' as username1,
    'Mot de passe: 12345678' as password1,
    'Email: admin@uom.cd' as email1,
    '' as separator2,
    'SUPER ADMINISTRATEUR:' as admin2,
    'Username: superadmin' as username2,
    'Mot de passe: admin123' as password2,
    'Email: superadmin@uom.cd' as email2,
    '' as separator3,
    'DIRECTEUR:' as admin3,
    'Username: directeur' as username3,
    'Mot de passe: directeur123' as password3,
    'Email: directeur@uom.cd' as email3,
    '' as separator4,
    'URL DE CONNEXION: http://127.0.0.1:8000/login/' as url;
