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

class RegistroTrabajadorForm(UserCreationForm):

    #Creo la lista de posibles rolea a crear por parte del dueño
    GRUPOS = [
        ("Administrador", "Administrador"),
        ("Empleado", "Empleado"),
    ]
    #Estructura de como se va  a mostrar el campo
    grupo = forms.ChoiceField(choices = GRUPOS, label = "Rol")
    #Hago el dni sea obligatorio para usuario administrador o empleado
    dni = forms.CharField(max_length = 9, required = True, label = 'DNI/NIE')

    class Meta:
        model = Usuario
    
        fields = [
            'username',
            'dni',
            'email',
            'telefono',
            'grupo',
        ]

class EditarTrabajadorForm(forms.ModelForm):

    GRUPOS = [
        ("Administrador", "Administrador"),
        ("Empleado", "Empleado"),
    ]

    grupo = forms.ChoiceField(
        choices=GRUPOS,
        label="Rol"
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'dni',
            'email',
            'telefono',
            'grupo',
        ]

class EditarPerfilForm(forms.ModelForm):

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'telefono',
        ]