from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
import csv
from .models import CustomUser, StudentProfile, TeacherProfile, Faculte, Promotion
from .forms import (
    CustomLoginForm, PasswordChangeFirstLoginForm, ProfileCompletionForm,
    StudentCreationForm, TeacherCreationForm, BulkStudentImportForm,
    StudentProfileForm
)


def user_login(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        if request.user.is_admin_user() or request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.is_teacher():
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Permettre la connexion via matricule OU username
            auth_username = identifier
            try:
                mapped_user = CustomUser.objects.filter(
                    Q(matricule__iexact=identifier) | Q(username__iexact=identifier)
                ).only('username').first()
                if mapped_user:
                    auth_username = mapped_user.username
            except Exception:
                pass

            user = authenticate(request, username=auth_username, password=password)
            
            if user is not None:
                login(request, user)
                
                if user.is_first_login:
                    messages.info(request, "Première connexion détectée. Veuillez changer votre mot de passe.")
                    return redirect('first_login_password_change')
                
                if user.is_admin_user() or user.is_superuser:
                    return redirect('admin_dashboard')
                elif user.is_teacher():
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                messages.error(request, "Matricule ou mot de passe incorrect.")
        else:
            messages.error(request, "Matricule ou mot de passe incorrect.")
    else:
        form = CustomLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def user_logout(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')


@login_required
def first_login_password_change(request):
    """Vue de changement de mot de passe à la première connexion"""
    if not request.user.is_first_login:
        return redirect('admin_dashboard' if request.user.is_admin_user() else 'student_dashboard')
    
    if request.method == 'POST':
        form = PasswordChangeFirstLoginForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mot de passe changé avec succès. Veuillez compléter votre profil.")
            return redirect('first_login_profile_completion')
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PasswordChangeFirstLoginForm(request.user)
    
    return render(request, 'users/first_login_password.html', {'form': form})


@login_required
def first_login_profile_completion(request):
    """Vue de complétion du profil à la première connexion"""
    if not request.user.is_first_login:
        return redirect('admin_dashboard' if request.user.is_admin_user() else 'student_dashboard')
    
    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Marquer que la première connexion est terminée
            request.user.is_first_login = False
            request.user.is_active_student = True
            request.user.save()
            messages.success(request, "Profil complété avec succès ! Bienvenue sur MyUOM.")
            
            if request.user.is_admin_user():
                return redirect('admin_dashboard')
            elif request.user.is_teacher():
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
    else:
        form = ProfileCompletionForm(instance=request.user)
    
    return render(request, 'users/first_login_profile.html', {'form': form})


@login_required
def student_dashboard(request):
    """Tableau de bord étudiant"""
    if not request.user.is_student():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    # Import des modèles des autres apps avec gestion d'erreur
    try:
        from cours.models import InscriptionCours
        cours_available = True
    except:
        cours_available = False
    
    try:
        from travaux.models import Travail
        travaux_available = True
    except:
        travaux_available = False
    
    try:
        from resultats.models import Note
        notes_available = True
    except:
        notes_available = False
    
    # Statistiques avec gestion d'erreur
    if cours_available:
        try:
            mes_cours_count = InscriptionCours.objects.filter(
                etudiant=request.user, 
                is_actif=True
            ).count()
        except:
            mes_cours_count = 0
    else:
        mes_cours_count = 0
    
    if travaux_available:
        try:
            travaux_en_cours_count = Travail.objects.filter(
                statut='publie',
                is_visible_etudiants=True,
                niveau=request.user.student_profile.niveau if hasattr(request.user, 'student_profile') else 'L1'
            ).count()
        except:
            travaux_en_cours_count = 0
        
        # Travaux urgents (à rendre dans les 7 prochains jours)
        try:
            from django.utils import timezone
            from datetime import timedelta
            date_limite = timezone.now() + timedelta(days=7)
            
            travaux_urgents_count = Travail.objects.filter(
                statut='publie',
                is_visible_etudiants=True,
                date_limite_remise__lte=date_limite,
                niveau=request.user.student_profile.niveau if hasattr(request.user, 'student_profile') else 'L1'
            ).count()
        except:
            travaux_urgents_count = 0
    else:
        travaux_en_cours_count = 0
        travaux_urgents_count = 0
    
    # Moyenne générale (calcul simple)
    if notes_available:
        try:
            notes = Note.objects.filter(
                etudiant=request.user,
                is_publie=True
            )
            if notes.exists():
                moyenne_generale = round(sum(note.note_obtenue for note in notes) / notes.count(), 2)
            else:
                moyenne_generale = None
        except:
            moyenne_generale = None
    else:
        moyenne_generale = None
    
    # Mes cours récents
    if cours_available:
        try:
            mes_cours = InscriptionCours.objects.filter(
                etudiant=request.user,
                is_actif=True
            ).select_related('cours', 'cours__enseignant').order_by('-date_inscription')[:5]
        except:
            mes_cours = []
    else:
        mes_cours = []
    
    # Travaux à rendre
    if travaux_available:
        try:
            travaux_a_rendre = Travail.objects.filter(
                statut='publie',
                is_visible_etudiants=True,
                niveau=request.user.student_profile.niveau if hasattr(request.user, 'student_profile') else 'L1'
            ).select_related('enseignant').order_by('date_limite_remise')[:5]
        except:
            travaux_a_rendre = []
    else:
        travaux_a_rendre = []
    
    # Notifications (pour l'instant vide, on l'implémentera plus tard)
    notifications = []
    
    context = {
        'user': request.user,
        'mes_cours_count': mes_cours_count,
        'travaux_en_cours_count': travaux_en_cours_count,
        'travaux_urgents_count': travaux_urgents_count,
        'moyenne_generale': moyenne_generale,
        'mes_cours': mes_cours,
        'travaux_a_rendre': travaux_a_rendre,
        'notifications': notifications,
    }
    
    return render(request, 'users/student_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    """Tableau de bord enseignant"""
    if not request.user.is_teacher():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    return render(request, 'users/teacher_dashboard.html', {'user': request.user})


@login_required
def admin_dashboard(request):
    """Tableau de bord administrateur"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    total_students = CustomUser.objects.filter(user_type='etudiant').count()
    total_teachers = CustomUser.objects.filter(user_type='enseignant').count()
    active_students = CustomUser.objects.filter(user_type='etudiant', is_active_student=True).count()
    pending_first_login = CustomUser.objects.filter(is_first_login=True).count()
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'active_students': active_students,
        'pending_first_login': pending_first_login,
    }
    return render(request, 'users/admin_dashboard.html', context)


@login_required
def admin_student_list(request):
    """Liste des étudiants avec filtrage par faculté et promotion"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    search_query = request.GET.get('search', '')
    faculte_filter = request.GET.get('faculte', '')
    promotion_filter = request.GET.get('promotion', '')
    
    students = CustomUser.objects.filter(user_type='etudiant').select_related('student_profile')
    
    # Filtrage par recherche
    if search_query:
        students = students.filter(
            Q(matricule__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filtrage par faculté
    if faculte_filter:
        students = students.filter(student_profile__faculte__code=faculte_filter)
    
    # Filtrage par promotion
    if promotion_filter:
        # Parse la promotion (format: "2023-2024")
        try:
            annee_debut, annee_fin = promotion_filter.split('-')
            students = students.filter(
                student_profile__promotion__annee_debut=int(annee_debut),
                student_profile__promotion__annee_fin=int(annee_fin)
            )
        except (ValueError, AttributeError):
            pass  # Ignore les valeurs invalides
    
    # Tri
    order = request.GET.get('order', 'created')
    if order == 'name':
        students = students.order_by('last_name', 'first_name')
    elif order == 'matricule':
        students = students.order_by('matricule')
    elif order == 'faculte':
        students = students.order_by('student_profile__faculte', 'last_name')
    elif order == 'promotion':
        students = students.order_by('student_profile__promotion__annee_debut', 'last_name')
    else:
        students = students.order_by('-created_at')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(students, 10)
    try:
        students_page = paginator.page(page)
    except PageNotAnInteger:
        students_page = paginator.page(1)
    except EmptyPage:
        students_page = paginator.page(paginator.num_pages)

    # Options pour les filtres
    faculte_choices = [('', 'Toutes les facultés')] + [(f.code, f.nom) for f in Faculte.objects.filter(is_active=True).order_by('nom')]
    
    # Récupérer les promotions existantes
    existing_promotions = CustomUser.objects.filter(
        user_type='etudiant',
        student_profile__promotion__isnull=False
    ).values_list('student_profile__promotion__annee_debut', 'student_profile__promotion__annee_fin').distinct().order_by('student_profile__promotion__annee_debut')
    
    promotion_choices = [('', 'Toutes les promotions')] + [(f"{debut}-{fin}", f"{debut}-{fin}") for debut, fin in existing_promotions]
    
    return render(request, 'users/admin_student_list.html', {
        'students': students_page,
        'search_query': search_query,
        'faculte_filter': faculte_filter,
        'promotion_filter': promotion_filter,
        'faculte_choices': faculte_choices,
        'promotion_choices': promotion_choices,
        'order': order,
        'paginator': paginator,
    })


@login_required
def admin_student_create(request):
    """Création d'un étudiant"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            try:
                student = form.save()
                messages.success(request, f"Étudiant {student.matricule} créé avec succès.")
                return redirect('admin_student_list')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création : {str(e)}")
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = StudentCreationForm()
    
    return render(request, 'users/admin_student_create.html', {'form': form})


@login_required
def admin_student_detail(request, user_id):
    """Détails d'un étudiant"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    student = get_object_or_404(CustomUser, id=user_id, user_type='etudiant')
    return render(request, 'users/admin_student_detail.html', {'student': student})


@login_required
def admin_student_toggle_active(request, user_id):
    """Activer/Désactiver un compte étudiant"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    student = get_object_or_404(CustomUser, id=user_id, user_type='etudiant')
    student.is_active = not student.is_active
    student.save()
    
    status = "activé" if student.is_active else "désactivé"
    messages.success(request, f"Compte de {student.matricule} {status}.")
    return redirect('admin_student_list')


@login_required
def admin_student_reset_password(request, user_id):
    """Réinitialiser le mot de passe d'un étudiant"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    student = get_object_or_404(CustomUser, id=user_id, user_type='etudiant')
    default_password = "12345678"
    student.set_password(default_password)
    student.is_first_login = True
    student.save()
    
    messages.success(request, f"Mot de passe de {student.matricule} réinitialisé à {default_password}.")
    return redirect('admin_student_detail', user_id=user_id)


@login_required
def admin_student_bulk_import(request):
    """Importation en masse d'étudiants via CSV"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    if request.method == 'POST':
        form = BulkStudentImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            default_password = form.cleaned_data['default_password']
            
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                
                created_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        user = CustomUser.objects.create_user(
                            matricule=row['matricule'],
                            username=row['username'],
                            first_name=row.get('first_name', ''),
                            last_name=row.get('last_name', ''),
                            email=row.get('email', ''),
                            password=default_password,
                            user_type='etudiant',
                            is_first_login=True
                        )
                        
                        StudentProfile.objects.create(
                            user=user,
                            niveau=row.get('niveau', ''),
                            filiere=row.get('filiere', '')
                        )
                        
                        created_count += 1
                    except Exception:
                        error_count += 1
                
                messages.success(request, f"{created_count} étudiants importés. {error_count} erreurs.")
                return redirect('admin_student_list')
                
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
    else:
        form = BulkStudentImportForm()
    
    return render(request, 'users/admin_student_bulk_import.html', {'form': form})


@login_required
def admin_teacher_list(request):
    """Liste des enseignants"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    search_query = request.GET.get('search', '')
    teachers = CustomUser.objects.filter(user_type='enseignant')
    
    if search_query:
        teachers = teachers.filter(
            Q(matricule__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Tri
    order = request.GET.get('order', 'created')
    if order == 'name':
        teachers = teachers.order_by('last_name', 'first_name')
    elif order == 'matricule':
        teachers = teachers.order_by('matricule')
    else:
        teachers = teachers.order_by('-created_at')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(teachers, 10)
    try:
        teachers_page = paginator.page(page)
    except PageNotAnInteger:
        teachers_page = paginator.page(1)
    except EmptyPage:
        teachers_page = paginator.page(paginator.num_pages)

    return render(request, 'users/admin_teacher_list.html', {
        'teachers': teachers_page,
        'search_query': search_query,
        'order': order,
        'paginator': paginator,
    })


@login_required
def admin_teacher_create(request):
    """Création d'un enseignant"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Enseignant {teacher.matricule} créé avec succès.")
            return redirect('admin_teacher_list')
    else:
        form = TeacherCreationForm()
    
    return render(request, 'users/admin_teacher_create.html', {'form': form})


@login_required
def admin_teacher_detail(request, user_id):
    """Détails d'un enseignant"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    teacher = get_object_or_404(CustomUser, id=user_id, user_type='enseignant')
    return render(request, 'users/admin_teacher_detail.html', {'teacher': teacher})


# ======================== VUES ÉTUDIANT (LISTES) ========================

@login_required
def student_cours(request):
    """Redirection vers la liste des cours"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    return redirect('cours:student_cours_list')


@login_required
def student_cours_detail(request, cours_id):
    """Détails d'un cours pour l'étudiant avec les TP associés"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    # Récupérer le cours
    try:
        from cours.models import Cours
        cours = Cours.objects.get(
            id=cours_id,
            is_actif=True,
            is_visible_etudiants=True
        )
    except Cours.DoesNotExist:
        messages.error(request, "Cours non trouvé.")
        return redirect('cours:student_cours_list')
    
    # Vérifier que l'étudiant peut accéder à ce cours selon sa promotion, faculté et niveau
    try:
        student_profile = request.user.student_profile
        promotion = student_profile.promotion
        faculte = student_profile.faculte
        niveau_etudiant = student_profile.niveau
        
        # Vérifier la correspondance
        if cours.promotion and cours.promotion != promotion:
            messages.error(request, "Ce cours ne correspond pas à votre promotion.")
            return redirect('cours:student_cours_list')
        
        if cours.faculte and cours.faculte != faculte:
            messages.error(request, "Ce cours ne correspond pas à votre faculté.")
            return redirect('cours:student_cours_list')
        
        if cours.niveau and cours.niveau != niveau_etudiant:
            messages.error(request, "Ce cours ne correspond pas à votre niveau.")
            return redirect('cours:student_cours_list')
            
    except Exception as e:
        messages.error(request, "Profil étudiant incomplet. Veuillez contacter l'administrateur.")
        return redirect('cours:student_cours_list')
    
    # Récupérer les TP associés au cours
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
        
        # Récupérer les remises de l'étudiant pour ce cours
        remises = RemiseTravail.objects.filter(
            etudiant=request.user,
            travail__cours=cours
        ).select_related('travail')
        
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
                # Pas de remise encore
                if travail.is_remise_ouverte():
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
    
    context = {
        'cours': cours,
        'travaux_ouverts': travaux_ouverts,
        'travaux_fermes': travaux_fermes,
        'travaux_termines': travaux_termines,
        'supports_cours': supports_cours,
    }
    
    return render(request, 'users/student_cours_detail.html', context)


@login_required
def student_travaux(request):
    """Liste des travaux publiés et remises de l'étudiant selon sa promotion, faculté et niveau"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    try:
        from travaux.models import Travail, RemiseTravail
        from cours.models import Cours
        from django.utils import timezone

        # Récupérer les informations du profil étudiant
        student_profile = request.user.student_profile
        promotion = student_profile.promotion
        faculte = student_profile.faculte
        niveau_etudiant = student_profile.niveau

        # Récupérer les cours de l'étudiant selon sa promotion, faculté et niveau
        cours_etudiant = Cours.objects.filter(
            is_actif=True,
            is_visible_etudiants=True
        )
        
        if promotion:
            cours_etudiant = cours_etudiant.filter(promotion=promotion)
        if faculte:
            cours_etudiant = cours_etudiant.filter(faculte=faculte)
        if niveau_etudiant:
            cours_etudiant = cours_etudiant.filter(niveau=niveau_etudiant)

        # Récupérer les travaux des cours de l'étudiant
        travaux = Travail.objects.filter(
            cours__in=cours_etudiant,
            is_visible_etudiants=True,
            statut__in=['publie', 'ferme']
        ).select_related('cours', 'cours__enseignant').order_by('-date_creation')

        # Récupérer les remises de l'étudiant
        remises = RemiseTravail.objects.filter(
            etudiant=request.user,
            travail__in=travaux
        ).select_related('travail', 'travail__cours').order_by('-date_remise')

        # Créer un dictionnaire des remises par travail
        remises_dict = {remise.travail.id: remise for remise in remises}

        # Classer les travaux
        travaux_ouverts = []
        travaux_fermes = []
        travaux_termines = []

        for travail in travaux:
            remise = remises_dict.get(travail.id)
            
            if remise:
                if remise.statut in ['remis', 'en_cours_correction']:
                    travaux_ouverts.append((travail, remise))
                elif remise.statut in ['corrige', 'note_finalisee']:
                    travaux_termines.append((travail, remise))
            else:
                # Pas de remise encore
                if travail.is_remise_ouverte():
                    travaux_ouverts.append((travail, None))
                else:
                    travaux_fermes.append((travail, None))

    except Exception as e:
        travaux_ouverts = []
        travaux_fermes = []
        travaux_termines = []
        remises = []
        messages.warning(request, "Profil étudiant incomplet. Veuillez contacter l'administrateur.")

    return render(request, 'users/student_travaux.html', {
        'travaux_ouverts': travaux_ouverts,
        'travaux_fermes': travaux_fermes,
        'travaux_termines': travaux_termines,
        'remises': remises,
        'niveau_etudiant': getattr(request.user.student_profile, 'niveau', None) if hasattr(request.user, 'student_profile') else None,
        'now': timezone.now(),
    })


@login_required
def student_resultats(request):
    """Consultation des notes par UE et semestre"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    # Vérifier si les résultats sont activés
    try:
        from resultats.models import ConfigurationResultats
        if not ConfigurationResultats.get_resultats_actives():
            messages.info(request, "La consultation des résultats n'est pas encore activée.")
            return render(request, 'resultats/student_resultats_disabled.html')
    except:
        messages.info(request, "La consultation des résultats n'est pas encore activée.")
        return render(request, 'resultats/student_resultats_disabled.html')

    try:
        from resultats.models import Note, UE

        notes = (
            Note.objects
            .filter(etudiant=request.user, is_publie=True)
            .select_related('ue', 'enseignant')
            .order_by('ue__code', '-date_publication')
        )

        # Agrégation simple par UE
        ue_to_notes = {}
        for n in notes:
            ue_to_notes.setdefault(n.ue, []).append(n)
    except:
        ue_to_notes = {}

    return render(request, 'users/student_resultats.html', {
        'ue_to_notes': ue_to_notes,
    })


@login_required
def student_profil(request):
    """Informations personnelles et changement de mot de passe simple"""
    if not request.user.is_student():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    user_form = ProfileCompletionForm(request.POST or None, instance=request.user)
    profile = getattr(request.user, 'student_profile', None)
    profile_form = StudentProfileForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == 'POST':
        is_valid = user_form.is_valid() and profile_form.is_valid()
        if is_valid:
            user_form.save()
            sp = profile_form.save(commit=False)
            sp.user = request.user
            sp.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('student_profil')
        messages.error(request, "Veuillez corriger les erreurs.")

    return render(request, 'users/student_profil.html', {
        'form': user_form,
        'profile_form': profile_form,
    })


# ======================== GESTION FACULTÉS ET PROMOTIONS ========================

@login_required
def admin_faculte_list(request):
    """Liste des facultés"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    facultes = Faculte.objects.all().order_by('nom')
    return render(request, 'users/admin_faculte_list.html', {'facultes': facultes})


@login_required
def admin_promotion_list(request):
    """Liste des promotions"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    promotions = Promotion.objects.all().order_by('-annee_debut')
    return render(request, 'users/admin_promotion_list.html', {'promotions': promotions})


@login_required
def admin_student_data(request, user_id):
    """Récupérer les données d'un étudiant en JSON pour les modales"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        student = CustomUser.objects.get(id=user_id, user_type='etudiant')
        profile = student.student_profile
        
        data = {
            # Informations de base
            'username': student.username,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'birth_date': student.birth_date.strftime('%d/%m/%Y') if student.birth_date else '',
            'birth_place': student.birth_place or '',
            'phone': student.phone or '',
            'is_active': student.is_active,
            'created_at': student.created_at.strftime('%d/%m/%Y à %H:%M') if student.created_at else '',
            'last_login': student.last_login.strftime('%d/%m/%Y à %H:%M') if student.last_login else '',
            
            # Informations académiques
            'niveau': profile.niveau if profile else '',
            'filiere': profile.filiere if profile else '',
            'faculte': profile.faculte.code if profile and profile.faculte else '',
            'faculte_name': profile.faculte.nom if profile and profile.faculte else '',
            'promotion': profile.promotion.nom_complet if profile and profile.promotion else '',
            
            # Contact d'urgence
            'emergency_contact': profile.emergency_contact if profile else '',
            'emergency_phone': profile.emergency_phone if profile else '',
            
            # Photo
            'photo': profile.photo.url if profile and profile.photo else '',
        }
        return JsonResponse(data)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Étudiant non trouvé'}, status=404)


@login_required
def admin_student_edit(request, user_id):
    """Modifier un étudiant via modal"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    student = get_object_or_404(CustomUser, id=user_id, user_type='etudiant')
    
    if request.method == 'POST':
        # Mettre à jour les informations de base
        student.username = request.POST.get('username', student.username)
        student.first_name = request.POST.get('first_name', student.first_name)
        student.last_name = request.POST.get('last_name', student.last_name)
        student.email = request.POST.get('email', student.email)
        student.save()
        
        # Mettre à jour le profil étudiant
        if hasattr(student, 'student_profile'):
            profile = student.student_profile
            profile.niveau = request.POST.get('niveau', profile.niveau)
            profile.filiere = request.POST.get('filiere', profile.filiere)
            
            # Mettre à jour la faculté
            faculte_code = request.POST.get('faculte')
            if faculte_code:
                try:
                    faculte = Faculte.objects.get(code=faculte_code)
                    profile.faculte = faculte
                except Faculte.DoesNotExist:
                    pass
            
            # Mettre à jour la promotion
            promotion_str = request.POST.get('promotion')
            if promotion_str:
                try:
                    annee_debut, annee_fin = promotion_str.split('-')
                    promotion = Promotion.objects.get(annee_debut=int(annee_debut), annee_fin=int(annee_fin))
                    profile.promotion = promotion
                except (ValueError, Promotion.DoesNotExist):
                    pass
            
            profile.save()
        
        messages.success(request, f"Étudiant {student.matricule} modifié avec succès.")
        return redirect('admin_student_list')
    
    return redirect('admin_student_list')


@login_required
def admin_student_delete(request, user_id):
    """Supprimer un étudiant via modal"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    student = get_object_or_404(CustomUser, id=user_id, user_type='etudiant')
    
    if request.method == 'POST':
        matricule = student.matricule
        student.delete()
        messages.success(request, f"Étudiant {matricule} supprimé avec succès.")
        return redirect('admin_student_list')
    
    return redirect('admin_student_list')


# ======================== GESTION DES ENSEIGNANTS ========================

@login_required
def admin_teacher_list(request):
    """Liste des enseignants avec filtrage par faculté"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    search_query = request.GET.get('search', '')
    faculte_filter = request.GET.get('faculte', '')
    
    teachers = CustomUser.objects.filter(user_type='enseignant').select_related('teacher_profile')
    
    # Filtrage par recherche
    if search_query:
        teachers = teachers.filter(
            Q(matricule__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filtrage par faculté
    if faculte_filter:
        teachers = teachers.filter(teacher_profile__faculte__code=faculte_filter)
    
    # Tri
    order = request.GET.get('order', 'created')
    if order == 'name':
        teachers = teachers.order_by('last_name', 'first_name')
    elif order == 'matricule':
        teachers = teachers.order_by('matricule')
    elif order == 'faculte':
        teachers = teachers.order_by('teacher_profile__faculte__nom', 'last_name')
    else:
        teachers = teachers.order_by('-created_at')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(teachers, 10)
    try:
        teachers_page = paginator.page(page)
    except PageNotAnInteger:
        teachers_page = paginator.page(1)
    except EmptyPage:
        teachers_page = paginator.page(paginator.num_pages)

    # Options pour les filtres
    faculte_choices = [('', 'Toutes les facultés')] + [(f.code, f.nom) for f in Faculte.objects.filter(is_active=True).order_by('nom')]
    
    return render(request, 'users/admin_teacher_list.html', {
        'teachers': teachers_page,
        'search_query': search_query,
        'faculte_filter': faculte_filter,
        'faculte_choices': faculte_choices,
        'order': order,
        'paginator': paginator,
    })


@login_required
def admin_teacher_create(request):
    """Création d'un enseignant"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            try:
                teacher = form.save()
                messages.success(request, f"Enseignant {teacher.matricule} créé avec succès.")
                return redirect('admin_teacher_list')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création : {str(e)}")
        else:
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = TeacherCreationForm()
    
    return render(request, 'users/admin_teacher_create.html', {'form': form})


@login_required
def admin_teacher_data(request, user_id):
    """Récupérer les données d'un enseignant en JSON pour les modales"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        teacher = CustomUser.objects.get(id=user_id, user_type='enseignant')
        profile = teacher.teacher_profile
        
        data = {
            # Informations de base
            'username': teacher.username,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'email': teacher.email,
            'birth_date': teacher.birth_date.strftime('%d/%m/%Y') if teacher.birth_date else '',
            'birth_place': teacher.birth_place or '',
            'phone': teacher.phone or '',
            'is_active': teacher.is_active,
            'created_at': teacher.created_at.strftime('%d/%m/%Y à %H:%M') if teacher.created_at else '',
            'last_login': teacher.last_login.strftime('%d/%m/%Y à %H:%M') if teacher.last_login else '',
            
            # Informations professionnelles
            'department': profile.department if profile else '',
            'speciality': profile.speciality if profile else '',
            'office': profile.office if profile else '',
            'faculte': profile.faculte.code if profile and profile.faculte else '',
            'faculte_name': profile.faculte.nom if profile and profile.faculte else '',
        }
        return JsonResponse(data)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Enseignant non trouvé'}, status=404)


@login_required
def admin_teacher_edit(request, user_id):
    """Modifier un enseignant via modal"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    teacher = get_object_or_404(CustomUser, id=user_id, user_type='enseignant')
    
    if request.method == 'POST':
        # Mettre à jour les informations de base
        teacher.username = request.POST.get('username', teacher.username)
        teacher.first_name = request.POST.get('first_name', teacher.first_name)
        teacher.last_name = request.POST.get('last_name', teacher.last_name)
        teacher.email = request.POST.get('email', teacher.email)
        teacher.save()
        
        # Mettre à jour le profil enseignant
        if hasattr(teacher, 'teacher_profile'):
            profile = teacher.teacher_profile
            profile.department = request.POST.get('department', profile.department)
            profile.speciality = request.POST.get('speciality', profile.speciality)
            profile.office = request.POST.get('office', profile.office)
            
            # Mettre à jour la faculté
            faculte_code = request.POST.get('faculte')
            if faculte_code:
                try:
                    faculte = Faculte.objects.get(code=faculte_code)
                    profile.faculte = faculte
                except Faculte.DoesNotExist:
                    pass
            
            profile.save()
        
        messages.success(request, f"Enseignant {teacher.matricule} modifié avec succès.")
        return redirect('admin_teacher_list')
    
    return redirect('admin_teacher_list')


@login_required
def admin_teacher_delete(request, user_id):
    """Supprimer un enseignant via modal"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    teacher = get_object_or_404(CustomUser, id=user_id, user_type='enseignant')
    
    if request.method == 'POST':
        matricule = teacher.matricule
        teacher.delete()
        messages.success(request, f"Enseignant {matricule} supprimé avec succès.")
        return redirect('admin_teacher_list')
    
    return redirect('admin_teacher_list')


@login_required
def admin_teacher_toggle_active(request, user_id):
    """Activer/Désactiver un compte enseignant"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    teacher = get_object_or_404(CustomUser, id=user_id, user_type='enseignant')
    teacher.is_active = not teacher.is_active
    teacher.save()
    
    status = "activé" if teacher.is_active else "désactivé"
    messages.success(request, f"Enseignant {teacher.matricule} {status} avec succès.")
    return redirect('admin_teacher_list')


@login_required
def admin_teacher_reset_password(request, user_id):
    """Réinitialiser le mot de passe d'un enseignant"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    teacher = get_object_or_404(CustomUser, id=user_id, user_type='enseignant')
    default_password = "12345678"
    teacher.set_password(default_password)
    teacher.is_first_login = True
    teacher.save()

    messages.success(request, f"Mot de passe de {teacher.matricule} réinitialisé à {default_password}.")
    return redirect('admin_teacher_list')


# ======================== GESTION DES FACULTÉS ET PROMOTIONS ========================

@login_required
def admin_faculte_list(request):
    """Liste des facultés"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    facultes = Faculte.objects.all().order_by('nom')
    
    return render(request, 'users/admin_faculte_list.html', {
        'facultes': facultes,
    })


@login_required
def admin_promotion_list(request):
    """Liste des promotions"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    promotions = Promotion.objects.all().order_by('-annee_debut')
    
    return render(request, 'users/admin_promotion_list.html', {
        'promotions': promotions,
    })

