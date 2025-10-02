from django import forms
from .models import Cours, SupportCours
from users.models import CustomUser, Faculte, Promotion


class CoursCreationForm(forms.ModelForm):
    """Formulaire de création d'un cours"""
    
    class Meta:
        model = Cours
        fields = ['titre', 'code', 'description', 'type_cours', 'niveau', 'filiere', 'enseignant', 'faculte', 'promotion', 'date_debut', 'date_fin']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Introduction à la programmation'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: INFO101'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du cours'}),
            'type_cours': forms.Select(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-control'}),
            'filiere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Informatique'}),
            'enseignant': forms.Select(attrs={'class': 'form-control'}),
            'faculte': forms.Select(attrs={'class': 'form-control'}),
            'promotion': forms.Select(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'titre': 'Titre du cours',
            'code': 'Code du cours',
            'description': 'Description',
            'type_cours': 'Type de cours',
            'niveau': 'Niveau',
            'filiere': 'Filière',
            'enseignant': 'Enseignant responsable',
            'faculte': 'Faculté',
            'promotion': 'Promotion',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Définir les querysets pour les champs de relation
        self.fields['enseignant'].queryset = CustomUser.objects.filter(user_type='enseignant', is_active=True).order_by('last_name', 'first_name')
        self.fields['faculte'].queryset = Faculte.objects.filter(is_active=True).order_by('nom')
        self.fields['promotion'].queryset = Promotion.objects.filter(is_active=True).order_by('-annee_debut')
        
        # Rendre les champs facultatifs
        self.fields['enseignant'].required = False
        self.fields['faculte'].required = False
        self.fields['promotion'].required = False


class SupportCoursForm(forms.ModelForm):
    """Formulaire pour ajouter un support de cours"""
    
    class Meta:
        model = SupportCours
        fields = ['titre', 'description', 'type_support', 'fichier', 'is_public', 'ordre_affichage']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Cours 1 - Introduction'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description du support'}),
            'type_support': forms.Select(attrs={'class': 'form-control'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.ppt,.pptx,.txt'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordre_affichage': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
        labels = {
            'titre': 'Titre du support',
            'description': 'Description',
            'type_support': 'Type de support',
            'fichier': 'Fichier',
            'is_public': 'Visible pour les étudiants',
            'ordre_affichage': 'Ordre d\'affichage',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ordre_affichage'].initial = 0