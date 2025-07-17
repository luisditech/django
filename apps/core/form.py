from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'email', 'username', 'name', 'role',
            'is_active', 'is_staff', 'is_superuser', 'is_blocked', 'is_deleted'
        )

class CustomUserChangeForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        required=False,
        widget=forms.PasswordInput,
        help_text="Deja vacío si no quieres cambiar la contraseña."
    )

    class Meta:
        model = User
        fields = (
            'email', 'username', 'name', 'role', 'password',
            'is_active', 'is_staff', 'is_superuser', 'is_blocked', 'is_deleted'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_password = self.cleaned_data.get('password')

        if raw_password:
            user.set_password(raw_password)  # 🔐 hash si se cambia
        elif user.pk:
            # mantener la contraseña anterior si no se ingresó nada nuevo
            user.password = User.objects.get(pk=user.pk).password

        if commit:
            user.save()
        return user
