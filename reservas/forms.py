from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            'nombre_cliente',
            'telefono_cliente',
            'correo_cliente',
            'fecha_hora_inicio',
            'num_personas',
            'notas',
        ]
        widgets = {
            'fecha_hora_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }