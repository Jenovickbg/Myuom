-- Script SQL pour réinitialiser la base de données MyUOM
-- ATTENTION: Ce script va supprimer toutes les données !

-- Supprimer les tables dans l'ordre correct (en respectant les contraintes de clés étrangères)
DROP TABLE IF EXISTS users_studentprofile;
DROP TABLE IF EXISTS users_teacherprofile;
DROP TABLE IF EXISTS users_customuser;
DROP TABLE IF EXISTS users_faculte;
DROP TABLE IF EXISTS users_promotion;

-- Recréer les tables avec les nouvelles structures
-- (Les migrations Django vont s'occuper de cela)

-- Vider les autres tables si nécessaire
DELETE FROM cours_inscriptioncours;
DELETE FROM cours_supportcours;
DELETE FROM cours_cours;
DELETE FROM travaux_remisetravail;
DELETE FROM travaux_travail;
DELETE FROM resultats_inscriptionue;
DELETE FROM resultats_note;
DELETE FROM resultats_bulletin;
DELETE FROM resultats_ue;
