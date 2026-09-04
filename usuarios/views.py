from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from .forms import RegistroClienteForm


# Registrar un nuevo cliente
def agregar_usuario(request):

    if request.method == 'POST':
        # Creo el formulario con los datos enviados
        formulario = RegistroClienteForm(request.POST)

        # Valido que los datos ingresados sean correctos
        if formulario.is_valid():

            # Guardo el nuevo usuario y recupero el objeto creado
            usuario = formulario.save()

            # Busco el grupo "Cliente" creado previamente
            # desde el panel de administración de Django
            grupo_cliente = Group.objects.get(name='Cliente')

            # Agrego el usuario recién registrado al grupo Cliente
            usuario.groups.add(grupo_cliente)

            # Envio al cliente al login
            return redirect('login')

    else:

        # Si entra por primera vez a la página,
        # creo un formulario vacío
        formulario = RegistroClienteForm()

    # Envío el formulario al template para poder mostrarlo
    return render(request, 'usuarios/cliente/agregar_cliente.html', {'formulario': formulario})

def iniciar_sesion(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            # Inicio la sesión del usuario
            login(request, usuario)

            # Redirección temporal para comprobar el login
            return redirect('inicio')

        else:
            # Si authenticate devuelve None, las credenciales no son válidas
            error = 'Usuario o contraseña incorrectos'

    return render(request, 'usuarios/login.html', {'error': error})

def inicio(request):
    return render(request, 'usuarios/inicio.html')

def cerrar_sesion(request):
    logout(request)

    return redirect('login')