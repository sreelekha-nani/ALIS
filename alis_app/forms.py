from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=False) # Make optional in form validation, we'll sync it

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'role', 'email')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        
        # Sync email and username if one is missing (template uses 'username' for email)
        if username and not email:
            cleaned_data['email'] = username
            self.errors.pop('email', None) # Clear "required" error if we're fixing it here
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('name', '')
        # Ensure email is set from whatever we have
        email = self.cleaned_data.get('email') or self.cleaned_data.get('username')
        user.email = email
        user.username = email # Keep them in sync for simplicity
        
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.TextInput(attrs={'autofocus': True}))
