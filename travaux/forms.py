from django import forms
from django.contrib.auth import get_user_model
from .models import Travail

User = get_user_model()


class TravailForm(forms.ModelForm):
    class Meta:
        model = Travail
        fields = [
            'titre', 'description', 'consignes', 'type_travail', 'niveau', 'filiere',
            'date_limite_remise', 'date_limite_correction', 'note_maximale', 'coefficient',
            'is_visible_etudiants', 'fichier_consignes'
        ]
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du travail'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du travail'}),
            'consignes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Consignes pour les étudiants'}),
            'type_travail': forms.Select(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-control'}),
            'filiere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filière concernée'}),
            'date_limite_remise': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_limite_correction': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'note_maximale': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 20, 'step': 0.1}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.1}),
            'is_visible_etudiants': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fichier_consignes': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.ppt,.pptx,.zip,.rar'}),
        }
        labels = {
            'titre': 'Titre',
            'description': 'Description',
            'consignes': 'Consignes',
            'type_travail': 'Type de travail',
            'niveau': 'Niveau',
            'filiere': 'Filière',
            'date_limite_remise': 'Date limite de remise',
            'date_limite_correction': 'Date limite de correction',
            'note_maximale': 'Note maximale',
            'coefficient': 'Coefficient',
            'is_visible_etudiants': 'Visible pour les étudiants',
            'fichier_consignes': 'Fichier de consignes (optionnel)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Valeurs par défaut
        if not self.instance.pk:
            self.fields['note_maximale'].initial = 20
            self.fields['coefficient'].initial = 1
            self.fields['is_visible_etudiants'].initial = True

    def clean_fichier_consignes(self):
        f = self.cleaned_data.get('fichier_consignes')
        if not f:
            return f
        # Taille max ~ 10 Mo
        max_bytes = 10 * 1024 * 1024
        if f.size > max_bytes:
            raise forms.ValidationError('Le fichier dépasse 10 Mo.')
        return f

    def clean(self):
        cleaned_data = super().clean()
        date_limite_remise = cleaned_data.get('date_limite_remise')
        date_limite_correction = cleaned_data.get('date_limite_correction')
        
        if date_limite_remise and date_limite_correction:
            if date_limite_correction <= date_limite_remise:
                raise forms.ValidationError("La date limite de correction doit être postérieure à la date limite de remise.")
        
        return cleaned_data
