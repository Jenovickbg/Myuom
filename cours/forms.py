from django import forms
from django.contrib.auth import get_user_model
from .models import SupportCours, Cours

User = get_user_model()


class SupportCoursForm(forms.ModelForm):
    class Meta:
        model = SupportCours
        fields = ['cours', 'titre', 'description', 'type_support', 'fichier', 'is_public', 'ordre_affichage']
        widgets = {
            'cours': forms.Select(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du support'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description (optionnel)'}),
            'type_support': forms.Select(attrs={'class': 'form-control'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.ppt,.pptx,.zip,.rar,.png,.jpg,.jpeg'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordre_affichage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'cours': 'Cours',
            'titre': 'Titre',
            'description': 'Description',
            'type_support': 'Type',
            'fichier': 'Fichier',
            'is_public': 'Visible pour les étudiants',
            'ordre_affichage': "Ordre d'affichage",
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher is not None:
            self.fields['cours'].queryset = Cours.objects.filter(enseignant=teacher, is_actif=True)

    def clean_fichier(self):
        f = self.cleaned_data.get('fichier')
        if not f:
            return f
        # Taille max ~ 20 Mo
        max_bytes = 20 * 1024 * 1024
        if f.size > max_bytes:
            raise forms.ValidationError('Le fichier dépasse 20 Mo.')
        return f
