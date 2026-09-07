from django import forms
from .models import Usuario
from django.contrib.auth.forms import UserCreationForm

class RegistroClienteForm(UserCreationForm):
        # Campo contraseña personalizado
    password1 = forms.CharField(
        label = 'Contraseña',
        widget = forms.PasswordInput(
            attrs = {'class': 'form-control', 'placeholder': 'Ingresa una contraseña'})
    )

    # Campo confirmación de contraseña personalizado
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Repite la contraseña'})
    )

    class Meta:
        model = Usuario

        fields = [
            'username',
            'email',
            'telefono',
        ]
        widgets = {
            'username': forms.TextInput(attrs = {'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs = {'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs = {'class': 'form-control', 'placeholder': 'Teléfono'}),
        }

class RegistroTrabajadorForm(UserCreationForm):

    #Creo la lista de posibles rolea a crear por parte del dueño
    GRUPOS = [
        ("Administrador", "Administrador"),
        ("Empleado", "Empleado"),
    ]
    #Estructura de como se va  a mostrar el campo
    grupo = forms.ChoiceField(choices = GRUPOS, label = "Rol",  widget=forms.Select(attrs = {'class': 'form-select'}))
    #Hago el dni sea obligatorio para usuario administrador o empleado
    dni = forms.CharField(max_length = 9, required = True, label = 'DNI/NIE', widget=forms.TextInput(attrs = {'class': 'form-control', 'placeholder': 'DNI/NIE'}))

    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs = {'class': 'form-control', 'placeholder': 'Ingresa una contraseña'}))

    password2 = forms.CharField(label='Confirmar contraseña', widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repite la contraseña'}))

    class Meta:
        model = Usuario
    
        fields = [
            'username',
            'dni',
            'email',
            'telefono',
            'grupo',
        ]

        #Estilos Bootstrap para los campos del modelo Usuario
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'Nombre de usuario'}),

            'email': forms.EmailInput(attrs={'class': 'form-control',
                                             'placeholder': 'correo@ejemplo.com'}),

            'telefono': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'Teléfono'}),
        }


class EditarTrabajadorForm(forms.ModelForm):

    GRUPOS = [
        ("Administrador", "Administrador"),
        ("Empleado", "Empleado"),
    ]

    grupo = forms.ChoiceField(
        choices=GRUPOS,
        label="Rol",
        widget=forms.Select(attrs = {'class': 'form-select'})
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

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'Nombre de usuario'}),

            'dni': forms.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'DNI/NIE'}),
        
            'email': forms.EmailInput(attrs={'class': 'form-control',
                                             'placeholder': 'correo@ejemplo.com'}),
        
            'telefono': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'Teléfono'}),
        }

class EditarPerfilForm(forms.ModelForm):

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'telefono',
        ]