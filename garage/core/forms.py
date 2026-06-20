from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    nom = forms.CharField(max_length=100, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")


    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('nom', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Un compte avec cet e-mail existe déjà.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data.get('email')
        user.username = email
        user.email = email
        if commit:
            user.save()
        return user
    
# Mandova ilay custom mba afahany mitondra fanovana @ ireo voalaza :  

    # Le formulaire CustomUserCreationForm hérite de UserCreationForm de Django et apporte les personnalisations suivantes :

        # •  Champs supplémentaires : nom et email
        # •  Validation d'unicité de l'email — empêche deux comptes avec le même email
        # •  L'email est utilisé comme username → connexion par email au lieu du nom d'utilisateur classique
        # •  Méthode save() surchargée pour assigner email à username automatiquement
