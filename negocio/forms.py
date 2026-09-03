from django import forms
from .models import Negocio


class NegocioForm(forms.ModelForm):
    class Meta:
        model = Negocio
        fields = [
            'documento',
            'nombre',
            'direccion',
            'activo',
        ]