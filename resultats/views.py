from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q, Avg, Sum
from django.conf import settings
import os

from .models import UE, Note, InscriptionUE, Bulletin, ConfigurationResultats
from users.models import CustomUser


@login_required
def student_resultats(request):
    """Page des résultats pour l'étudiant"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    # Vérifier si les résultats sont activés
    if not ConfigurationResultats.get_resultats_actives():
        messages.info(request, "La consultation des résultats n'est pas encore activée.")
        return render(request, 'resultats/student_resultats_disabled.html')
    
    # Récupérer les inscriptions de l'étudiant
    inscriptions = InscriptionUE.objects.filter(
        etudiant=request.user,
        is_actif=True,
        is_valide=True
    ).select_related('ue')
    
    # Récupérer les notes de l'étudiant
    notes = Note.objects.filter(
        etudiant=request.user,
        is_publie=True
    ).select_related('ue', 'enseignant').order_by('-date_publication')
    
    # Calculer les moyennes par UE
    moyennes_ue = {}
    for inscription in inscriptions:
        ue_notes = notes.filter(ue=inscription.ue)
        if ue_notes.exists():
            # Calculer la moyenne pondérée
            total_pondere = sum(note.get_moyenne_ponderee() for note in ue_notes)
            total_coefficients = sum(note.coefficient for note in ue_notes)
            if total_coefficients > 0:
                moyenne = total_pondere / total_coefficients
                moyennes_ue[inscription.ue.id] = {
                    'ue': inscription.ue,
                    'moyenne': round(moyenne, 2),
                    'notes': ue_notes,
                    'total_coefficients': total_coefficients
                }
    
    # Récupérer les bulletins
    bulletins = Bulletin.objects.filter(
        etudiant=request.user,
        is_publie=True
    ).order_by('-date_publication')
    
    context = {
        'inscriptions': inscriptions,
        'notes': notes,
        'moyennes_ue': moyennes_ue,
        'bulletins': bulletins,
    }
    
    return render(request, 'resultats/student_resultats.html', context)


@login_required
def student_bulletin_pdf(request, bulletin_id):
    """Génération du PDF du bulletin"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    bulletin = get_object_or_404(Bulletin, id=bulletin_id, etudiant=request.user)
    
    # Récupérer les notes du bulletin
    notes = Note.objects.filter(
        etudiant=request.user,
        ue__semestre=bulletin.semestre,
        is_publie=True
    ).select_related('ue', 'enseignant').order_by('ue__code')
    
    # Calculer les moyennes par UE
    moyennes_ue = {}
    for note in notes:
        ue_id = note.ue.id
        if ue_id not in moyennes_ue:
            moyennes_ue[ue_id] = {
                'ue': note.ue,
                'notes': [],
                'total_pondere': 0,
                'total_coefficients': 0
            }
        
        moyennes_ue[ue_id]['notes'].append(note)
        moyennes_ue[ue_id]['total_pondere'] += note.get_moyenne_ponderee()
        moyennes_ue[ue_id]['total_coefficients'] += note.coefficient
    
    # Calculer les moyennes finales
    for ue_id, data in moyennes_ue.items():
        if data['total_coefficients'] > 0:
            data['moyenne'] = round(data['total_pondere'] / data['total_coefficients'], 2)
        else:
            data['moyenne'] = 0
    
    context = {
        'bulletin': bulletin,
        'etudiant': request.user,
        'moyennes_ue': moyennes_ue,
        'notes': notes,
    }
    
    # Générer le HTML du bulletin
    html_content = render_to_string('resultats/bulletin_pdf.html', context)
    
    # Pour l'instant, on retourne le HTML (on peut ajouter weasyprint plus tard)
    return HttpResponse(html_content, content_type='text/html')


@login_required
def admin_resultats_settings(request):
    """Paramètres des résultats pour l'admin"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    if request.method == 'POST':
        # Activer/désactiver les résultats
        resultats_actives = request.POST.get('resultats_actives') == 'on'
        
        # Mettre à jour la configuration en base de données
        ConfigurationResultats.set_resultats_actives(resultats_actives, request.user)
        messages.success(request, f"Résultats {'activés' if resultats_actives else 'désactivés'} avec succès.")
        return redirect('resultats:admin_resultats_settings')
    
    # Vérifier l'état actuel
    resultats_actives = ConfigurationResultats.get_resultats_actives()
    
    context = {
        'resultats_actives': resultats_actives,
    }
    
    return render(request, 'resultats/admin_resultats_settings.html', context)


@login_required
def admin_ue_list(request):
    """Liste des UE pour l'admin"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    ues = UE.objects.all().order_by('niveau', 'semestre', 'code')
    
    context = {
        'ues': ues,
    }
    
    return render(request, 'resultats/admin_ue_list.html', context)


@login_required
def admin_notes_list(request):
    """Liste des notes pour l'admin"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    notes = Note.objects.select_related('etudiant', 'ue', 'enseignant').order_by('-date_publication')
    
    context = {
        'notes': notes,
    }
    
    return render(request, 'resultats/admin_notes_list.html', context)