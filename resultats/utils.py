"""
Utilitaires pour le calcul automatique des cotes étudiants
"""
from django.db.models import Avg, Sum, Count, Q
from decimal import Decimal

def calculer_cote_etudiant(etudiant, annee_academique, semestre):
    """
    Calcule automatiquement la cote d'un étudiant basée sur:
    - Sa faculté
    - Sa promotion
    - Les cours qu'il a suivis
    - Ses notes obtenues
    """
    from resultats.models import Note, UE, CoteEtudiant
    from cours.models import Cours
    
    # Vérifier que l'étudiant a un profil
    if not hasattr(etudiant, 'student_profile'):
        return None
    
    student_profile = etudiant.student_profile
    faculte = student_profile.faculte
    promotion = student_profile.promotion
    niveau = student_profile.niveau
    
    if not faculte or not promotion or not niveau:
        return None
    
    # Récupérer tous les cours de l'étudiant selon sa faculté, promotion et niveau
    cours_etudiant = Cours.objects.filter(
        faculte=faculte,
        promotion=promotion,
        niveau=niveau,
        is_actif=True
    )
    
    # Récupérer toutes les UEs correspondant aux cours de l'étudiant
    # On suppose que les UEs sont liées aux cours par la filière et le niveau
    ues_etudiant = UE.objects.filter(
        niveau=niveau,
        semestre=semestre,
        is_actif=True,
        is_visible_etudiants=True
    )
    
    # Récupérer les notes de l'étudiant pour ces UEs
    notes = Note.objects.filter(
        etudiant=etudiant,
        ue__in=ues_etudiant,
        is_publie=True
    ).select_related('ue').order_by('ue__code', '-date_publication')
    
    # Regrouper les notes par UE et calculer la moyenne par UE
    ue_notes = {}
    for note in notes:
        if note.ue.code not in ue_notes:
            ue_notes[note.ue.code] = {
                'ue': note.ue,
                'notes': [],
                'moyenne_ue': 0,
                'credits': note.ue.credits,
                'valide': False
            }
        ue_notes[note.ue.code]['notes'].append(note)
    
    # Calculer les statistiques globales
    total_ues = len(ue_notes)
    total_credits_obtenus = 0
    total_credits_possible = 0
    nombre_ue_validees = 0
    nombre_ue_a_reprendre = 0
    somme_moyennes = 0
    
    for ue_code, ue_data in ue_notes.items():
        notes_ue = ue_data['notes']
        credits_ue = ue_data['credits']
        total_credits_possible += credits_ue
        
        # Calculer la moyenne de l'UE (avec coefficients)
        if notes_ue:
            total_note_ponderee = sum(n.note_obtenue * n.coefficient for n in notes_ue)
            total_coefficient = sum(n.coefficient for n in notes_ue)
            moyenne_ue = float(total_note_ponderee / total_coefficient) if total_coefficient > 0 else 0
            ue_data['moyenne_ue'] = moyenne_ue
            
            # Vérifier si l'UE est validée (>= 10)
            if moyenne_ue >= 10:
                ue_data['valide'] = True
                nombre_ue_validees += 1
                total_credits_obtenus += credits_ue
                somme_moyennes += moyenne_ue
            else:
                nombre_ue_a_reprendre += 1
                somme_moyennes += moyenne_ue
    
    # Calculer la moyenne générale
    moyenne_generale = float(somme_moyennes / total_ues) if total_ues > 0 else 0
    
    # Calculer la mention automatiquement
    mention = CoteEtudiant.calculer_mention(moyenne_generale)
    
    # Calculer la décision automatiquement
    decision = CoteEtudiant.calculer_decision(moyenne_generale, nombre_ue_a_reprendre)
    
    # Générer une observation automatique
    observation = generer_observation(moyenne_generale, nombre_ue_validees, total_ues)
    
    # Créer ou mettre à jour la cote
    cote, created = CoteEtudiant.objects.update_or_create(
        etudiant=etudiant,
        annee_academique=annee_academique,
        semestre=semestre,
        defaults={
            'moyenne': Decimal(str(round(moyenne_generale, 2))),
            'total_credits': total_credits_obtenus,
            'total_credits_possible': total_credits_possible,
            'mention': mention,
            'decision': decision,
            'nombre_ue_a_reprendre': nombre_ue_a_reprendre,
            'observation': observation,
            'is_definitif': False  # Par défaut, la cote n'est pas définitive
        }
    )
    
    return cote


def generer_observation(moyenne, ue_validees, total_ues):
    """Génère une observation automatique selon les résultats"""
    if moyenne >= 16:
        return "Excellent travail! Continuez ainsi."
    elif moyenne >= 14:
        return "Bon travail! Résultats satisfaisants."
    elif moyenne >= 12:
        return "Résultats corrects. Continuez vos efforts."
    elif moyenne >= 10:
        return f"Résultats acceptables. {ue_validees}/{total_ues} UE validées."
    elif moyenne >= 8:
        return f"Résultats insuffisants. Reprenez les UE non validées."
    else:
        return f"Résultats très insuffisants. Redoublement recommandé."


def recalculer_toutes_cotes(annee_academique, semestre):
    """
    Recalcule toutes les cotes pour tous les étudiants
    pour une année académique et un semestre donnés
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    etudiants = User.objects.filter(user_type='etudiant', is_active=True)
    
    resultats = {
        'total': 0,
        'success': 0,
        'errors': []
    }
    
    for etudiant in etudiants:
        try:
            cote = calculer_cote_etudiant(etudiant, annee_academique, semestre)
            if cote:
                resultats['success'] += 1
            resultats['total'] += 1
        except Exception as e:
            resultats['errors'].append({
                'etudiant': etudiant.matricule,
                'erreur': str(e)
            })
            resultats['total'] += 1
    
    return resultats


def valider_cote(cote_id, valideur):
    """
    Valide une cote (la marque comme définitive)
    """
    from resultats.models import CoteEtudiant
    
    try:
        cote = CoteEtudiant.objects.get(id=cote_id)
        cote.is_definitif = True
        cote.cree_par = valideur
        cote.save()
        return True
    except CoteEtudiant.DoesNotExist:
        return False

