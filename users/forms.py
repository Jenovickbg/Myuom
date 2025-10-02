from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import CustomUser, StudentProfile, TeacherProfile, Faculte, Promotion

User = get_user_model()


class CustomLoginForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    username = forms.CharField(
        label="Matricule",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'UOM2025-001'
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )


class PasswordChangeFirstLoginForm(forms.Form):
    """Formulaire de changement de mot de passe à la première connexion"""
    old_password = forms.CharField(
        label="Ancien mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe temporaire'
        })
    )
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe'
        }),
        help_text="Minimum 8 caractères"
    )
    new_password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("L'ancien mot de passe est incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
            if len(password1) < 8:
                raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        return cleaned_data

    def save(self):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


class ProfileCompletionForm(forms.ModelForm):
    """Formulaire de complétion du profil à la première connexion et édition d'infos personnelles"""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'birth_date', 'birth_place', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (optionnel)'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'birth_place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu de naissance'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
            'birth_date': 'Date de naissance',
            'birth_place': 'Lieu de naissance',
            'phone': 'Téléphone',
        }

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        birth_date = cleaned_data.get('birth_date')
        birth_place = cleaned_data.get('birth_place')

        if not first_name or not last_name:
            raise forms.ValidationError("Le prénom et le nom sont obligatoires.")
        
        if not birth_date:
            raise forms.ValidationError("La date de naissance est obligatoire.")
        
        if not birth_place:
            raise forms.ValidationError("Le lieu de naissance est obligatoire.")
        
        return cleaned_data


class StudentProfileForm(forms.ModelForm):
    """Édition des informations académiques de l'étudiant (restreint)"""
    class Meta:
        model = StudentProfile
        fields = ['photo', 'emergency_contact', 'emergency_phone']  # Retiré niveau, filiere, faculte, promotion
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom du contact d'urgence"}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Téléphone d'urgence"}),
        }
        labels = {
            'photo': 'Photo de profil',
            'emergency_contact': "Contact d'urgence",
            'emergency_phone': "Téléphone d'urgence",
        }


class StudentCreationForm(forms.ModelForm):
    """Formulaire de création d'un étudiant par l'admin (sans mot de passe)"""
    niveau = forms.ChoiceField(
        label="Niveau",
        choices=[
            ('', '-- Sélectionner --'),
            ('L1', 'Licence 1'),
            ('L2', 'Licence 2'),
            ('L3', 'Licence 3'),
            ('M1', 'Master 1'),
            ('M2', 'Master 2'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    filiere = forms.CharField(
        label="Filière",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Informatique'})
    )
    
    faculte = forms.ModelChoiceField(
        label="Faculté",
        queryset=Faculte.objects.none(),  # Sera défini dans __init__
        empty_label="-- Sélectionner --",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    promotion = forms.ModelChoiceField(
        label="Promotion",
        queryset=Promotion.objects.none(),  # Sera défini dans __init__
        empty_label="-- Sélectionner --",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['matricule', 'username', 'first_name', 'last_name', 'email', 'user_type']
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UOM2025-001'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Identifiant'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'user_type': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].initial = 'etudiant'
        
        # Définir les querysets pour les champs de relation
        self.fields['faculte'].queryset = Faculte.objects.filter(is_active=True).order_by('nom')
        self.fields['promotion'].queryset = Promotion.objects.filter(is_active=True).order_by('-annee_debut')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'etudiant'
        user.is_first_login = True
        # Définir le mot de passe par défaut
        user.set_password('12345678')
        
        if commit:
            user.save()
            # Créer le profil étudiant
            StudentProfile.objects.create(
                user=user,
                niveau=self.cleaned_data['niveau'],
                filiere=self.cleaned_data['filiere'],
                faculte=self.cleaned_data['faculte'],
                promotion=self.cleaned_data['promotion']
            )
        
        return user


class TeacherCreationForm(UserCreationForm):
    """Formulaire de création d'un enseignant par l'admin"""
    department = forms.CharField(
        label="Département",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Informatique'})
    )
    
    speciality = forms.CharField(
        label="Spécialité",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Réseaux'})
    )

    class Meta:
        model = CustomUser
        fields = ['matricule', 'username', 'first_name', 'last_name', 'email', 'user_type']
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UOM2025-E001'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Identifiant'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'user_type': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].initial = 'enseignant'
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'enseignant'
        user.is_first_login = True
        
        if commit:
            user.save()
            # Créer le profil enseignant
            TeacherProfile.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                speciality=self.cleaned_data['speciality']
            )
        
        return user


class BulkStudentImportForm(forms.Form):
    """Formulaire d'importation en masse d'étudiants (CSV)"""
    csv_file = forms.FileField(
        label="Fichier CSV",
        help_text="Format: matricule,username,first_name,last_name,email,niveau,filiere",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    default_password = forms.CharField(
        label="Mot de passe par défaut",
        initial="123456",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


