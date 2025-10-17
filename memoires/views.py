from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q

from .models import Memoire, CertificatMemoire
from users.models import CustomUser


# ==================== VUES ÉTUDIANTS ====================

@login_required
def student_memoire_dashboard(request):
    """Dashboard des mémoires pour l'étudiant"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    # Vérifier le niveau de l'étudiant
    try:
        niveau = request.user.student_profile.niveau
        if niveau not in ['L3', 'M2']:
            messages.error(request, "Le système de mémoire n'est accessible qu'aux étudiants de L3 et M2.")
            return redirect('student_dashboard')
    except:
        messages.error(request, "Profil étudiant incomplet.")
        return redirect('student_dashboard')
    
    # Récupérer le mémoire de l'étudiant (s'il existe)
    memoire = Memoire.objects.filter(etudiant=request.user).first()
    
    context = {
        'memoire': memoire,
        'niveau': niveau,
    }
    return render(request, 'memoires/student_dashboard.html', context)


@login_required
def student_soumettre_sujet(request):
    """Soumettre un sujet de mémoire"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    # Vérifier si l'étudiant a déjà un mémoire
    memoire_existant = Memoire.objects.filter(etudiant=request.user).first()
    if memoire_existant and memoire_existant.statut not in ['brouillon', 'refuse']:
        messages.warning(request, "Vous avez déjà un sujet de mémoire soumis.")
        return redirect('memoires:student_memoire_dashboard')
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        objectifs = request.POST.get('objectifs')
        domaine = request.POST.get('domaine')
        domaine_autre = request.POST.get('domaine_autre', '')
        commentaire = request.POST.get('commentaire_etudiant', '')
        
        if not all([titre, description, objectifs, domaine]):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('memoires:student_memoire_dashboard')
        
        # Mettre à jour ou créer le mémoire
        if memoire_existant and memoire_existant.statut in ['brouillon', 'refuse']:
            # Mettre à jour le mémoire existant
            memoire_existant.titre = titre
            memoire_existant.description = description
            memoire_existant.objectifs = objectifs
            memoire_existant.domaine = domaine
            memoire_existant.domaine_autre = domaine_autre if domaine == 'autre' else ''
            memoire_existant.commentaire_etudiant = commentaire
            memoire_existant.statut = 'soumis'
            memoire_existant.date_soumission_sujet = timezone.now()
            memoire_existant.save()
            messages.success(request, "✅ Votre sujet de mémoire a été soumis avec succès pour validation.")
        else:
            # Créer un nouveau mémoire
            Memoire.objects.create(
                etudiant=request.user,
                titre=titre,
                description=description,
                objectifs=objectifs,
                domaine=domaine,
                domaine_autre=domaine_autre if domaine == 'autre' else '',
                commentaire_etudiant=commentaire,
                statut='soumis'
            )
            messages.success(request, "✅ Votre sujet de mémoire a été soumis avec succès pour validation.")
        
        return redirect('memoires:student_memoire_dashboard')
    
    # Si GET, rediriger vers le dashboard (car c'est une modale)
    return redirect('memoires:student_memoire_dashboard')


@login_required
def student_deposer_memoire(request):
    """Déposer le mémoire final en PDF"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    memoire = get_object_or_404(Memoire, etudiant=request.user)
    
    if not memoire.peut_deposer_final():
        messages.error(request, "Vous ne pouvez pas déposer votre mémoire final tant que votre sujet n'est pas validé.")
        return redirect('memoires:student_memoire_dashboard')
    
    if request.method == 'POST':
        fichier_pdf = request.FILES.get('fichier_memoire')
        
        if not fichier_pdf:
            messages.error(request, "Veuillez sélectionner un fichier PDF.")
        elif not fichier_pdf.name.endswith('.pdf'):
            messages.error(request, "Le fichier doit être au format PDF.")
        else:
            memoire.fichier_memoire = fichier_pdf
            memoire.date_depot_final = timezone.now()
            memoire.statut = 'termine'
            memoire.save()
            messages.success(request, "✅ Votre mémoire a été déposé avec succès. Vous pouvez maintenant lancer la vérification anti-plagiat.")
            return redirect('memoires:student_memoire_dashboard')
    
    # Si GET, rediriger vers le dashboard (tout se fait via modale)
    return redirect('memoires:student_memoire_dashboard')


@login_required
def student_verifier_plagiat(request):
    """Lancer la vérification anti-plagiat"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    memoire = get_object_or_404(Memoire, etudiant=request.user)
    
    if memoire.statut != 'termine' or not memoire.fichier_memoire:
        messages.error(request, "Vous devez d'abord déposer votre mémoire final.")
        return redirect('memoires:student_memoire_dashboard')
    
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        
        if confirmation == 'oui':
            # Lancer la vérification anti-plagiat
            est_valide = memoire.lancer_verification_plagiat()
            
            if est_valide:
                messages.success(request, f"✅ Vérification terminée ! Score de plagiat : {memoire.score_plagiat:.2f}% (Acceptable). Vous pouvez maintenant confirmer et obtenir votre certificat.")
            else:
                messages.warning(request, f"⚠️ Score de plagiat : {memoire.score_plagiat:.2f}% - Veuillez revoir votre travail.")
            
            return redirect('memoires:student_memoire_dashboard')
        else:
            messages.info(request, "Vérification annulée.")
            return redirect('memoires:student_memoire_dashboard')
    
    # Si GET, rediriger vers le dashboard (tout se fait via modale)
    return redirect('memoires:student_memoire_dashboard')


@login_required
def student_confirmer_final(request):
    """Confirmer que le travail est terminé et générer le certificat"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    memoire = get_object_or_404(Memoire, etudiant=request.user)
    
    if not memoire.plagiat_verifie or memoire.score_plagiat >= 20:
        messages.error(request, "Votre mémoire doit d'abord passer la vérification anti-plagiat avec succès.")
        return redirect('memoires:student_memoire_dashboard')
    
    if request.method == 'POST':
        confirmation_finale = request.POST.get('confirmation_finale')
        
        if confirmation_finale == 'oui':
            # Générer le certificat
            if not hasattr(memoire, 'certificat'):
                numero_certificat = CertificatMemoire.generer_numero()
                annee_academique = '2024-2025'  # À rendre dynamique
                
                CertificatMemoire.objects.create(
                    memoire=memoire,
                    numero_certificat=numero_certificat,
                    annee_academique=annee_academique
                )
            
            memoire.statut = 'certifie'
            memoire.date_certification = timezone.now()
            memoire.save()
            
            messages.success(request, "🎉 Félicitations ! Votre certificat de dépôt a été généré avec succès.")
            return redirect('memoires:student_telecharger_certificat')
        else:
            messages.info(request, "Confirmation annulée.")
            return redirect('memoires:student_memoire_dashboard')
    
    # Si GET, rediriger vers le dashboard (tout se fait via modale)
    return redirect('memoires:student_memoire_dashboard')


@login_required
def student_telecharger_certificat(request):
    """Télécharger le certificat de dépôt en PDF"""
    if not request.user.is_student_user():
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    memoire = get_object_or_404(Memoire, etudiant=request.user)
    
    if not hasattr(memoire, 'certificat'):
        messages.error(request, "Aucun certificat disponible.")
        return redirect('memoires:student_memoire_dashboard')
    
    certificat = memoire.certificat
    
    try:
        from xhtml2pdf import pisa
        from django.conf import settings
        import os
        
        # Contexte pour le template
        context = {
            'certificat': certificat,
            'memoire': memoire,
            'etudiant': request.user,
            'student_profile': request.user.student_profile,
            'logo_path': os.path.join(settings.STATIC_ROOT, 'images', 'logo-UOM.jpg') if settings.STATIC_ROOT else '',
        }
        
        # Render template
        template = render_to_string('memoires/certificat_pdf.html', context)
        
        # Créer le PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificat_{certificat.numero_certificat}.pdf"'
        
        # Générer le PDF
        pisa_status = pisa.CreatePDF(template, dest=response)
        
        if pisa_status.err:
            messages.error(request, "Erreur lors de la génération du PDF.")
            return redirect('memoires:student_memoire_dashboard')
        
        return response
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération du certificat : {str(e)}")
        return redirect('memoires:student_memoire_dashboard')


# ==================== VUES ADMIN ====================

@login_required
def admin_memoires_list(request):
    """Liste des mémoires pour l'admin"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    # Filtres
    statut_filter = request.GET.get('statut', '')
    niveau_filter = request.GET.get('niveau', '')
    search_query = request.GET.get('search', '')
    
    memoires = Memoire.objects.all().select_related('etudiant', 'directeur', 'encadreur').order_by('-date_soumission_sujet')
    
    if statut_filter:
        memoires = memoires.filter(statut=statut_filter)
    
    if niveau_filter:
        memoires = memoires.filter(etudiant__student_profile__niveau=niveau_filter)
    
    if search_query:
        memoires = memoires.filter(
            Q(titre__icontains=search_query) |
            Q(etudiant__first_name__icontains=search_query) |
            Q(etudiant__last_name__icontains=search_query) |
            Q(etudiant__matricule__icontains=search_query)
        )
    
    # Récupérer la liste des enseignants pour attribution
    enseignants = CustomUser.objects.filter(user_type='enseignant', is_active=True).order_by('last_name', 'first_name')
    
    context = {
        'memoires': memoires,
        'enseignants': enseignants,
        'statut_filter': statut_filter,
        'niveau_filter': niveau_filter,
        'search_query': search_query,
    }
    return render(request, 'memoires/admin_memoires_list.html', context)


@login_required
def admin_valider_memoire(request, memoire_id):
    """Valider un sujet de mémoire et attribuer encadrement"""
    if not request.user.is_admin_user() and not request.user.is_superuser:
        messages.error(request, "Accès non autorisé.")
        return redirect('login')
    
    memoire = get_object_or_404(Memoire, id=memoire_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'valider':
            directeur_id = request.POST.get('directeur')
            encadreur_id = request.POST.get('encadreur')
            commentaire = request.POST.get('commentaire_admin', '')
            
            if not directeur_id:
                messages.error(request, "Veuillez sélectionner un directeur de mémoire.")
            else:
                memoire.directeur_id = directeur_id
                if encadreur_id:
                    memoire.encadreur_id = encadreur_id
                memoire.commentaire_admin = commentaire
                memoire.statut = 'valide'
                memoire.date_validation = timezone.now()
                memoire.save()
                messages.success(request, f"Sujet validé et encadrement attribué pour {memoire.etudiant.get_full_name()}.")
        
        elif action == 'refuser':
            motif = request.POST.get('motif_refus', '')
            
            if not motif:
                messages.error(request, "Veuillez indiquer un motif de refus.")
            else:
                memoire.statut = 'refuse'
                memoire.motif_refus = motif
                memoire.save()
                messages.success(request, f"Sujet refusé pour {memoire.etudiant.get_full_name()}.")
        
        return redirect('memoires:admin_memoires_list')
    
    # Enseignants pour le formulaire
    enseignants = CustomUser.objects.filter(user_type='enseignant', is_active=True).order_by('last_name', 'first_name')
    
    context = {
        'memoire': memoire,
        'enseignants': enseignants,
    }
    return render(request, 'memoires/admin_valider_memoire.html', context)

