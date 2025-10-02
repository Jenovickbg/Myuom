from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from .models import Cours, SupportCours, InscriptionCours
from users.models import CustomUser, Faculte, Promotion
from .forms import CoursCreationForm, SupportCoursForm


# ======================== VUES ADMINISTRATEUR ========================

@login_required
def admin_cours_list(request):
    """Liste des cours avec filtrage par faculté et promotion"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    search_query = request.GET.get('search', '')
    faculte_filter = request.GET.get('faculte', '')
    promotion_filter = request.GET.get('promotion', '')
    
    cours = Cours.objects.select_related('enseignant', 'faculte', 'promotion')
    
    # Filtrage par recherche
    if search_query:
        cours = cours.filter(
            Q(titre__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(enseignant__first_name__icontains=search_query) |
            Q(enseignant__last_name__icontains=search_query)
        )
    
    # Filtrage par faculté
    if faculte_filter:
        cours = cours.filter(faculte__code=faculte_filter)
    
    # Filtrage par promotion
    if promotion_filter:
        try:
            annee_debut, annee_fin = promotion_filter.split('-')
            cours = cours.filter(
                promotion__annee_debut=int(annee_debut),
                promotion__annee_fin=int(annee_fin)
            )
        except (ValueError, AttributeError):
            pass
    
    # Tri
    order = request.GET.get('order', 'created')
    if order == 'titre':
        cours = cours.order_by('titre')
    elif order == 'code':
        cours = cours.order_by('code')
    elif order == 'enseignant':
        cours = cours.order_by('enseignant__last_name', 'enseignant__first_name')
    elif order == 'faculte':
        cours = cours.order_by('faculte__nom', 'titre')
    elif order == 'promotion':
        cours = cours.order_by('promotion__annee_debut', 'titre')
    else:
        cours = cours.order_by('-date_creation')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(cours, 10)
    try:
        cours_page = paginator.page(page)
    except PageNotAnInteger:
        cours_page = paginator.page(1)
    except EmptyPage:
        cours_page = paginator.page(paginator.num_pages)

    # Options pour les filtres
    faculte_choices = [('', 'Toutes les facultés')] + [(f.code, f.nom) for f in Faculte.objects.filter(is_active=True).order_by('nom')]
    
    # Récupérer les promotions existantes
    existing_promotions = Cours.objects.filter(
        promotion__isnull=False
    ).values_list('promotion__annee_debut', 'promotion__annee_fin').distinct().order_by('promotion__annee_debut')

    promotion_choices = [('', 'Toutes les promotions')] + [(f"{debut}-{fin}", f"{debut}-{fin}") for debut, fin in existing_promotions]
    
    # Récupérer la liste des enseignants pour les formulaires
    enseignants = CustomUser.objects.filter(user_type='enseignant', is_active=True).order_by('last_name', 'first_name')
    
    return render(request, 'cours/admin_cours_list.html', {
        'cours': cours_page,
        'search_query': search_query,
        'faculte_filter': faculte_filter,
        'promotion_filter': promotion_filter,
        'faculte_choices': faculte_choices,
        'promotion_choices': promotion_choices,
        'enseignants': enseignants,
        'order': order,
        'paginator': paginator,
    })


@login_required
def admin_cours_create(request):
    """Création d'un cours"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    if request.method == 'POST':
        form = CoursCreationForm(request.POST)
        if form.is_valid():
            try:
                cours = form.save()
                messages.success(request, f"Cours {cours.code} créé avec succès.")
                return redirect('cours:admin_cours_list')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création : {str(e)}")
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CoursCreationForm()
    
    return render(request, 'cours/admin_cours_create.html', {'form': form})


@login_required
def admin_cours_data(request, cours_id):
    """Récupérer les données d'un cours en JSON pour les modales"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        cours = Cours.objects.get(id=cours_id)
        
        data = {
            'titre': cours.titre,
            'code': cours.code,
            'description': cours.description or '',
            'type_cours': cours.type_cours,
            'niveau': cours.niveau,
            'filiere': cours.filiere,
            'enseignant_id': cours.enseignant.id,
            'enseignant_name': cours.enseignant.get_full_name(),
            'faculte': cours.faculte.code if cours.faculte else '',
            'faculte_name': cours.faculte.nom if cours.faculte else '',
            'promotion': cours.promotion.nom_complet if cours.promotion else '',
            'date_debut': cours.date_debut.strftime('%Y-%m-%d') if cours.date_debut else '',
            'date_fin': cours.date_fin.strftime('%Y-%m-%d') if cours.date_fin else '',
            'is_actif': cours.is_actif,
            'is_visible_etudiants': cours.is_visible_etudiants,
            'date_creation': cours.date_creation.strftime('%d/%m/%Y à %H:%M') if cours.date_creation else '',
        }
        return JsonResponse(data)
    except Cours.DoesNotExist:
        return JsonResponse({'error': 'Cours non trouvé'}, status=404)


@login_required
def admin_cours_edit(request, cours_id):
    """Modifier un cours via modal"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    cours = get_object_or_404(Cours, id=cours_id)
    
    if request.method == 'POST':
        # Mettre à jour les informations de base
        cours.titre = request.POST.get('titre', cours.titre)
        cours.code = request.POST.get('code', cours.code)
        cours.description = request.POST.get('description', cours.description)
        cours.type_cours = request.POST.get('type_cours', cours.type_cours)
        cours.niveau = request.POST.get('niveau', cours.niveau)
        cours.filiere = request.POST.get('filiere', cours.filiere)
        
        # Mettre à jour l'enseignant
        enseignant_id = request.POST.get('enseignant')
        if enseignant_id:
            try:
                enseignant = CustomUser.objects.get(id=enseignant_id, user_type='enseignant')
                cours.enseignant = enseignant
            except CustomUser.DoesNotExist:
                pass
        
        # Mettre à jour la faculté
        faculte_code = request.POST.get('faculte')
        if faculte_code:
            try:
                faculte = Faculte.objects.get(code=faculte_code)
                cours.faculte = faculte
            except Faculte.DoesNotExist:
                pass
        
        # Mettre à jour la promotion
        promotion_str = request.POST.get('promotion')
        if promotion_str:
            try:
                annee_debut, annee_fin = promotion_str.split('-')
                promotion = Promotion.objects.get(annee_debut=int(annee_debut), annee_fin=int(annee_fin))
                cours.promotion = promotion
            except (ValueError, Promotion.DoesNotExist):
                pass
        
        # Mettre à jour les dates
        date_debut = request.POST.get('date_debut')
        if date_debut:
            cours.date_debut = date_debut
        
        date_fin = request.POST.get('date_fin')
        if date_fin:
            cours.date_fin = date_fin
        
        cours.save()
        
        messages.success(request, f"Cours {cours.code} modifié avec succès.")
        return redirect('cours:admin_cours_list')
    
    return redirect('admin_cours_list')


@login_required
def admin_cours_delete(request, cours_id):
    """Supprimer un cours via modal"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    cours = get_object_or_404(Cours, id=cours_id)
    
    if request.method == 'POST':
        code = cours.code
        cours.delete()
        messages.success(request, f"Cours {code} supprimé avec succès.")
        return redirect('cours:admin_cours_list')
    
    return redirect('admin_cours_list')


@login_required
def admin_cours_toggle_active(request, cours_id):
    """Activer/Désactiver un cours"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    cours = get_object_or_404(Cours, id=cours_id)
    cours.is_actif = not cours.is_actif
    cours.save()
    
    status = "activé" if cours.is_actif else "désactivé"
    messages.success(request, f"Cours {cours.code} {status} avec succès.")
    return redirect('admin_cours_list')


# ======================== VUES ENSEIGNANT ========================

@login_required
def teacher_cours_list(request):
    """Liste des cours d'un enseignant"""
    if not request.user.is_teacher_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    cours = Cours.objects.filter(enseignant=request.user).order_by('-date_creation')
    
    return render(request, 'cours/teacher_courses.html', {
        'cours': cours,
    })


@login_required
def teacher_cours_detail(request, cours_id):
    """Détails d'un cours pour l'enseignant avec les TP/TD et supports"""
    if not request.user.is_teacher_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    # Récupérer le cours
    try:
        cours = Cours.objects.get(
            id=cours_id,
            enseignant=request.user,
            is_actif=True
        )
    except Cours.DoesNotExist:
        messages.error(request, "Cours non trouvé.")
        return redirect('cours:teacher_cours_list')

    # Récupérer les TP/TD associés au cours
    travaux_ouverts = []
    travaux_fermes = []
    travaux_termines = []

    try:
        from travaux.models import Travail, RemiseTravail
        from django.utils import timezone

        # Récupérer tous les travaux du cours
        travaux = Travail.objects.filter(
            cours=cours,
            is_visible_etudiants=True,
            statut__in=['publie', 'ferme']
        ).order_by('-date_creation')

        # Récupérer les remises pour ce cours
        remises = RemiseTravail.objects.filter(
            travail__cours=cours
        ).select_related('travail', 'etudiant')

        # Créer un dictionnaire des remises par travail
        remises_dict = {remise.travail.id: remise for remise in remises}

        # Classer les travaux
        for travail in travaux:
            remise = remises_dict.get(travail.id)

            if remise:
                if remise.statut in ['remis', 'en_cours_correction']:
                    travaux_ouverts.append((travail, remise))
                elif remise.statut in ['corrige', 'note_finalisee']:
                    travaux_termines.append((travail, remise))
            else:
                # Pas de remise encore - vérifier si la date limite est dépassée
                from django.utils import timezone
                if travail.date_limite_remise and travail.date_limite_remise > timezone.now():
                    travaux_ouverts.append((travail, None))
                else:
                    travaux_fermes.append((travail, None))

    except Exception as e:
        messages.info(request, "La section des travaux n'est pas encore disponible.")

    # Récupérer les supports de cours
    supports_cours = []
    try:
        from cours.models import SupportCours
        supports_cours = SupportCours.objects.filter(
            cours=cours,
            is_public=True
        ).order_by('ordre_affichage', '-date_publication')
    except Exception:
        pass

    # Statistiques
    total_travaux = len(travaux_ouverts) + len(travaux_fermes) + len(travaux_termines)
    total_remises = len([r for _, r in travaux_ouverts if r]) + len([r for _, r in travaux_termines if r])

    context = {
        'cours': cours,
        'travaux_ouverts': travaux_ouverts,
        'travaux_fermes': travaux_fermes,
        'travaux_termines': travaux_termines,
        'supports_cours': supports_cours,
        'total_travaux': total_travaux,
        'total_remises': total_remises,
    }

    return render(request, 'cours/teacher_cours_detail.html', context)


@login_required
def teacher_cours_create(request):
    """Création d'un cours par un enseignant"""
    if not request.user.is_teacher_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    if request.method == 'POST':
        form = CoursCreationForm(request.POST)
        if form.is_valid():
            cours = form.save(commit=False)
            cours.enseignant = request.user
            cours.save()
            messages.success(request, f"Cours {cours.code} créé avec succès.")
            return redirect('cours:teacher_cours_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CoursCreationForm()
    
    return render(request, 'cours/teacher_cours_create.html', {'form': form})


# ======================== VUES ÉTUDIANT ========================

@login_required
def student_cours_list(request):
    """Liste des cours disponibles pour un étudiant selon sa promotion et faculté"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    # Récupérer les informations du profil étudiant
    try:
        student_profile = request.user.student_profile
        promotion = student_profile.promotion
        faculte = student_profile.faculte
        niveau_etudiant = student_profile.niveau  # L1, L2, L3, M1, M2, etc.
    except:
        promotion = None
        faculte = None
        niveau_etudiant = None
        messages.warning(request, "Profil étudiant incomplet. Veuillez contacter l'administrateur.")
        return render(request, 'cours/student_cours_list.html', {
            'cours': [],
            'promotion': None,
            'faculte': None,
            'niveau_etudiant': None,
        })
    
    # Filtrer les cours selon la promotion, faculté ET niveau de l'étudiant
    cours = Cours.objects.filter(
        is_actif=True,
        is_visible_etudiants=True
    )
    
    # Filtrage par promotion
    if promotion:
        cours = cours.filter(promotion=promotion)
    
    # Filtrage par faculté
    if faculte:
        cours = cours.filter(faculte=faculte)
    
    # Filtrage par niveau (L1, L2, L3, M1, M2, etc.)
    if niveau_etudiant:
        cours = cours.filter(niveau=niveau_etudiant)
    
    cours = cours.order_by('-date_creation')
    
    return render(request, 'cours/student_cours_list.html', {
        'cours': cours,
        'promotion': promotion,
        'faculte': faculte,
        'niveau_etudiant': niveau_etudiant,
    })


@login_required
def student_cours_detail(request, cours_id):
    """Détails d'un cours pour un étudiant"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    cours = get_object_or_404(Cours, id=cours_id, is_actif=True, is_visible_etudiants=True)
    
    # Vérifier que l'étudiant peut accéder à ce cours
    try:
        student_profile = request.user.student_profile
        if cours.promotion and cours.promotion != student_profile.promotion:
            messages.error(request, "Vous n'avez pas accès à ce cours.")
            return redirect('cours:student_cours_list')
    except:
        pass
    
    # Récupérer les supports de cours
    supports = SupportCours.objects.filter(cours=cours, is_public=True).order_by('ordre_affichage', '-date_publication')
    
    # Vérifier si l'étudiant est inscrit
    is_inscrit = InscriptionCours.objects.filter(etudiant=request.user, cours=cours, is_actif=True).exists()
    
    return render(request, 'cours/student_cours_detail.html', {
        'cours': cours,
        'supports': supports,
        'is_inscrit': is_inscrit,
    })


@login_required
def student_cours_inscription(request, cours_id):
    """Inscription d'un étudiant à un cours"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    cours = get_object_or_404(Cours, id=cours_id, is_actif=True, is_visible_etudiants=True)
    
    # Vérifier que l'étudiant peut s'inscrire à ce cours
    try:
        student_profile = request.user.student_profile
        if cours.promotion and cours.promotion != student_profile.promotion:
            messages.error(request, "Vous n'avez pas accès à ce cours.")
            return redirect('cours:student_cours_list')
    except:
        pass
    
    # Créer ou réactiver l'inscription
    inscription, created = InscriptionCours.objects.get_or_create(
        etudiant=request.user,
        cours=cours,
        defaults={'is_actif': True, 'is_valide': False}
    )
    
    if not created:
        inscription.is_actif = True
        inscription.save()
    
    messages.success(request, f"Vous êtes maintenant inscrit au cours {cours.code}.")
    return redirect('cours:student_cours_detail', cours_id=cours_id)