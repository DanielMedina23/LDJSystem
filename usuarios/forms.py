from django import forms
from .models import Usuario
from django.contrib.auth.forms import UserCreationForm

class RegistroClienteForm(UserCreationForm):
    class Meta:
        model = Usuario

        fields = [
            'username',
            'email',
            'telefono',
        ]