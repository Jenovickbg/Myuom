from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Cours, SupportCours
from .forms import SupportCoursForm


@login_required
def teacher_courses(request):
    """Liste des cours de l'enseignant"""
    if not hasattr(request.user, 'user_type') or not request.user.is_teacher():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    cours_list = Cours.objects.filter(enseignant=request.user).order_by('code')
    supports_count = (
        SupportCours.objects
        .filter(enseignant=request.user)
        .values('cours').distinct().count()
    )

    context = {
        'cours_list': cours_list,
        'supports_count': supports_count,
    }
    return render(request, 'cours/teacher_courses.html', context)


@login_required
def support_create(request):
    """Publication d'un support de cours"""
    if not hasattr(request.user, 'user_type') or not request.user.is_teacher():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')

    if request.method == 'POST':
        form = SupportCoursForm(request.POST, request.FILES, teacher=request.user)
        if form.is_valid():
            support = form.save(commit=False)
            support.enseignant = request.user
            support.save()
            messages.success(request, "Support publié avec succès.")
            return redirect('cours:teacher_courses')
        messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = SupportCoursForm(teacher=request.user)

    return render(request, 'cours/support_create.html', {'form': form})

# Create your views here.
