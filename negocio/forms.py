from django import forms
from .models import Negocio, Mesa, Horario


class NegocioForm(forms.ModelForm):
    class Meta:
        model = Negocio
        fields = [
            'documento',
            'nombre',
            'direccion',
            'activo',
        ]

class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = [
            'nombre_interno',
            'capacidad',
            'activa',
        ]

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = [
            'dia_semana',
            'hora_apertura',
            'hora_cierre',
        ]