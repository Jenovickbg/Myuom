from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Travail, RemiseTravail
from .forms import TravailForm


@login_required
def teacher_travaux_list(request):
    """Liste des travaux de l'enseignant"""
    if not hasattr(request.user, 'user_type') or not request.user.is_teacher():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    travaux = Travail.objects.filter(enseignant=request.user).order_by('-date_creation')
    
    # Statistiques
    total_travaux = travaux.count()
    travaux_publies = travaux.filter(statut='publie').count()
    travaux_fermes = travaux.filter(statut='ferme').count()
    
    # Remises en attente
    remises_attente = RemiseTravail.objects.filter(
        travail__enseignant=request.user,
        statut='remis'
    ).count()

    context = {
        'travaux': travaux,
        'total_travaux': total_travaux,
        'travaux_publies': travaux_publies,
        'travaux_fermes': travaux_fermes,
        'remises_attente': remises_attente,
    }
    return render(request, 'travaux/teacher_travaux_list.html', context)


@login_required
def teacher_cours_selection(request):
    """Sélection du cours pour créer un travail"""
    if not hasattr(request.user, 'user_type') or not request.user.is_teacher():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    # Récupérer les cours de l'enseignant
    from cours.models import Cours
    cours = Cours.objects.filter(
        enseignant=request.user,
        is_actif=True
    ).order_by('titre')

    return render(request, 'travaux/teacher_cours_selection.html', {
        'cours': cours,
    })


@login_required
def teacher_travail_create(request, cours_id):
    """Création d'un travail pour un cours spécifique"""
    if not hasattr(request.user, 'user_type') or not request.user.is_teacher():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    # Vérifier que le cours appartient à l'enseignant
    from cours.models import Cours
    cours = get_object_or_404(Cours, id=cours_id, enseignant=request.user, is_actif=True)

    if request.method == 'POST':
        form = TravailForm(request.POST, request.FILES)
        if form.is_valid():
            travail = form.save(commit=False)
            travail.enseignant = request.user
            travail.cours = cours
            travail.save()
            messages.success(request, f"Travail créé avec succès pour le cours {cours.code}.")
            return redirect('travaux:teacher_travaux_list')
        messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = TravailForm()

    return render(request, 'travaux/teacher_travail_create.html', {
        'form': form,
        'cours': cours,
    })


@login_required
def teacher_travail_detail(request, travail_id):
    """Détails d'un travail et ses remises"""
    if not hasattr(request.user, 'user_type') or not request.user.is_teacher():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    travail = get_object_or_404(Travail, id=travail_id, enseignant=request.user)
    remises = RemiseTravail.objects.filter(travail=travail).order_by('-date_remise')
    
    # Statistiques
    total_remises = remises.count()
    remises_corrigees = remises.filter(statut='corrige').count()
    remises_en_attente = remises.filter(statut='remis').count()

    context = {
        'travail': travail,
        'remises': remises,
        'total_remises': total_remises,
        'remises_corrigees': remises_corrigees,
        'remises_en_attente': remises_en_attente,
    }
    return render(request, 'travaux/teacher_travail_detail.html', context)


@login_required
def teacher_travail_toggle_status(request, travail_id):
    """Publier/Fermer un travail"""
    if not hasattr(request.user, 'user_type') or not request.user.is_teacher():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    travail = get_object_or_404(Travail, id=travail_id, enseignant=request.user)
    
    if travail.statut == 'brouillon':
        travail.statut = 'publie'
        travail.date_publication = timezone.now()
        messages.success(request, f"Travail '{travail.titre}' publié.")
    elif travail.statut == 'publie':
        travail.statut = 'ferme'
        messages.success(request, f"Travail '{travail.titre}' fermé.")
    elif travail.statut == 'ferme':
        travail.statut = 'publie'
        messages.success(request, f"Travail '{travail.titre}' republié.")
    
    travail.save()
    return redirect('travaux:teacher_travail_detail', travail_id=travail.id)


@login_required
def teacher_remise_detail(request, remise_id):
    """Détails d'une remise pour correction"""
    if not hasattr(request.user, 'user_type') or not request.user.is_teacher():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    remise = get_object_or_404(RemiseTravail, id=remise_id, travail__enseignant=request.user)
    
    context = {
        'remise': remise,
    }
    return render(request, 'travaux/teacher_remise_detail.html', context)


@login_required
def student_rendre_travail(request, travail_id):
    """Permet à un étudiant de rendre un travail"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    travail = get_object_or_404(Travail, id=travail_id, is_visible_etudiants=True)
    
    # Vérifier si la remise est ouverte
    if not travail.is_remise_ouverte():
        messages.error(request, "La date limite de remise est dépassée.")
        return redirect('student_cours_detail', cours_id=travail.cours.id)
    
    # Vérifier si l'étudiant a déjà rendu ce travail
    remise_existante = RemiseTravail.objects.filter(
        etudiant=request.user,
        travail=travail
    ).first()
    
    if request.method == 'POST':
        fichier_principal = request.FILES.get('fichier_principal')
        fichier_supplementaire = request.FILES.get('fichier_supplementaire')
        commentaire = request.POST.get('commentaire_etudiant', '')
        
        if not fichier_principal:
            messages.error(request, "Vous devez joindre un fichier principal.")
        else:
            if remise_existante:
                # Mise à jour de la remise existante
                remise_existante.fichier_principal = fichier_principal
                if fichier_supplementaire:
                    remise_existante.fichiers_supplementaires = fichier_supplementaire
                remise_existante.commentaire_etudiant = commentaire
                remise_existante.date_modification = timezone.now()
                remise_existante.save()
                messages.success(request, "Votre travail a été mis à jour avec succès.")
            else:
                # Création d'une nouvelle remise
                remise = RemiseTravail.objects.create(
                    etudiant=request.user,
                    travail=travail,
                    fichier_principal=fichier_principal,
                    fichiers_supplementaires=fichier_supplementaire,
                    commentaire_etudiant=commentaire,
                    statut='remis'
                )
                messages.success(request, "Votre travail a été rendu avec succès.")
            
            return redirect('student_cours_detail', cours_id=travail.cours.id)
    
    context = {
        'travail': travail,
        'remise_existante': remise_existante,
    }
    return render(request, 'travaux/student_rendre_travail.html', context)