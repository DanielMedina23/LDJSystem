from datetime import timedelta
from django import forms
from django.utils import timezone
from .models import Reserva


class ReservaForm(forms.ModelForm):
    # Casillas de consentimiento obligatorias para cumplimiento legal (RGPD/LOPD)
    acepta_privacidad = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'Debes aceptar la política de privacidad para continuar.'}
    )
    acepta_cookies = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Reserva
        fields = [
            'mesa',
            'nombre_cliente',
            'telefono_cliente',
            'correo_cliente',
            'fecha_hora_inicio',
            'num_personas',
            'notas',
            'acepta_privacidad',
            'acepta_cookies',
        ]
        widgets = {
            'fecha_hora_inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Formatear la fecha para que el input HTML5 datetime-local la reconozca al editar
        if self.instance and self.instance.pk and self.instance.fecha_hora_inicio:
            self.initial['fecha_hora_inicio'] = self.instance.fecha_hora_inicio.strftime('%Y-%m-%dT%H:%M')

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.CheckboxInput):
                pass
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        mesa = cleaned_data.get('mesa')
        inicio = cleaned_data.get('fecha_hora_inicio')

        # 1. Validar fecha pasada solo en creación o si la fecha ha sido modificada
        if inicio and inicio < timezone.now():
            if not self.instance.pk or self.instance.fecha_hora_inicio != inicio:
                self.add_error('fecha_hora_inicio', 'No puedes programar una reserva en una fecha u hora pasada.')

        # 2. Validar colisiones de horario en la misma mesa
        if mesa and inicio:
            fin = inicio + timedelta(hours=2)
            estados_activos = ['activa',
                               'pendiente_confirmacion',
                               'pendiente_revision',
                               'confirmada',
                               'en_curso']
            
            colisiones = Reserva.objects.filter(
                mesa=mesa,
                estado__in=estados_activos,
                fecha_hora_inicio__lt=fin,
                fecha_hora_fin__gt=inicio
            )

            if self.instance and self.instance.pk:
                colisiones = colisiones.exclude(pk=self.instance.pk)

            if colisiones.exists():
                self.add_error('mesa', 'La mesa seleccionada coincide en horarios con otra reserva existente.')

        return cleaned_data