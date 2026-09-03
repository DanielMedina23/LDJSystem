from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            'usuario',
            'mesa',
            'nombre_invitado',
            'telefono_invitado',
            'correo_invitado',
            'fecha_hora_inicio',
            'fecha_hora_fin',
            'num_personas',
            'estado',
            'notas',
        ]
        widgets = {
            'fecha_hora_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_hora_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }