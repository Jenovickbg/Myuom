from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import csv
from .models import CustomUser, StudentProfile, TeacherProfile
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
            request.user.complete_first_login()
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
    
    # Import des modèles des autres apps
    from cours.models import InscriptionCours
    from travaux.models import Travail
    from resultats.models import Note
    
    # Statistiques
    mes_cours_count = InscriptionCours.objects.filter(
        etudiant=request.user, 
        is_actif=True
    ).count()
    
    travaux_en_cours_count = Travail.objects.filter(
        statut='publie',
        is_visible_etudiants=True,
        niveau=request.user.student_profile.niveau if hasattr(request.user, 'student_profile') else 'L1'
    ).count()
    
    # Travaux urgents (à rendre dans les 7 prochains jours)
    from django.utils import timezone
    from datetime import timedelta
    date_limite = timezone.now() + timedelta(days=7)
    
    travaux_urgents_count = Travail.objects.filter(
        statut='publie',
        is_visible_etudiants=True,
        date_limite_remise__lte=date_limite,
        niveau=request.user.student_profile.niveau if hasattr(request.user, 'student_profile') else 'L1'
    ).count()
    
    # Moyenne générale (calcul simple)
    notes = Note.objects.filter(
        etudiant=request.user,
        is_publie=True
    )
    if notes.exists():
        moyenne_generale = round(sum(note.note_obtenue for note in notes) / notes.count(), 2)
    else:
        moyenne_generale = None
    
    # Mes cours récents
    mes_cours = InscriptionCours.objects.filter(
        etudiant=request.user,
        is_actif=True
    ).select_related('cours', 'cours__enseignant').order_by('-date_inscription')[:5]
    
    # Travaux à rendre
    travaux_a_rendre = Travail.objects.filter(
        statut='publie',
        is_visible_etudiants=True,
        niveau=request.user.student_profile.niveau if hasattr(request.user, 'student_profile') else 'L1'
    ).select_related('enseignant').order_by('date_limite_remise')[:5]
    
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
    """Liste des étudiants"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    search_query = request.GET.get('search', '')
    students = CustomUser.objects.filter(user_type='etudiant')
    
    if search_query:
        students = students.filter(
            Q(matricule__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Tri
    order = request.GET.get('order', 'created')
    if order == 'name':
        students = students.order_by('last_name', 'first_name')
    elif order == 'matricule':
        students = students.order_by('matricule')
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

    return render(request, 'users/admin_student_list.html', {
        'students': students_page,
        'search_query': search_query,
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
            student = form.save()
            messages.success(request, f"Étudiant {student.matricule} créé avec succès.")
            return redirect('admin_student_list')
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
    default_password = "123456"
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
    """Liste des cours de l'étudiant (inscriptions) et supports récents"""
    if not request.user.is_student():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    from cours.models import InscriptionCours, SupportCours

    inscriptions = (
        InscriptionCours.objects
        .filter(etudiant=request.user, is_actif=True)
        .select_related('cours', 'cours__enseignant')
        .order_by('cours__code')
    )

    supports_recents = (
        SupportCours.objects
        .filter(is_public=True, cours__inscriptions__etudiant=request.user)
        .select_related('cours', 'enseignant')
        .order_by('-date_publication')[:10]
    )

    return render(request, 'users/student_cours.html', {
        'inscriptions': inscriptions,
        'supports_recents': supports_recents,
    })


@login_required
def student_travaux(request):
    """Liste des travaux publiés et remises de l'étudiant"""
    if not request.user.is_student():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    from travaux.models import Travail, RemiseTravail
    from django.utils import timezone

    profil_niveau = getattr(getattr(request.user, 'student_profile', None), 'niveau', None)

    travaux = (
        Travail.objects
        .filter(is_visible_etudiants=True, statut__in=['publie', 'ferme'])
        .filter(niveau=profil_niveau) if profil_niveau else Travail.objects.none()
    )

    remises = (
        RemiseTravail.objects
        .filter(etudiant=request.user)
        .select_related('travail')
        .order_by('-date_remise')
    )

    # Séparer en ouverts/fermés
    travaux_ouverts = [t for t in travaux if t.is_remise_ouverte()]
    travaux_fermes = [t for t in travaux if not t.is_remise_ouverte()]

    return render(request, 'users/student_travaux.html', {
        'travaux_ouverts': travaux_ouverts,
        'travaux_fermes': travaux_fermes,
        'remises': remises,
        'now': timezone.now(),
    })


@login_required
def student_resultats(request):
    """Consultation des notes par UE et semestre"""
    if not request.user.is_student():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

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

