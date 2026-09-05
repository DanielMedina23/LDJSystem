from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from usuarios.decorators import administrador_required
from .forms import EditarTrabajadorForm, RegistroClienteForm, RegistroTrabajadorForm, EditarPerfilForm
from .models import Usuario

#CLIENTES
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

#FIN CLIENTES

#TRABAJADORES

#Crear Trabajador
@administrador_required
def crear_trabajador(request):

    if request.method == 'POST':
        formulario = RegistroTrabajadorForm(request.POST)
    else:
        formulario = RegistroTrabajadorForm()

    # Si quien entra NO es superusuario,
    # solo puede crear empleados
    if not request.user.is_superuser:
        formulario.fields['grupo'].choices = [
            ('Empleado', 'Empleado')
        ]

    if request.method == 'POST' and formulario.is_valid():

        trabajador = formulario.save()

        grupo_seleccionado = formulario.cleaned_data['grupo']
        grupo = Group.objects.get(name=grupo_seleccionado)

        trabajador.groups.add(grupo)

        return redirect('ver_trabajadores')

    return render(request, 'usuarios/trabajador/crear_trabajador.html', {'formulario': formulario})

#Ver trabajadores
@administrador_required
def ver_trabajadores(request):

    if request.user.is_superuser:
        trabajadores = Usuario.objects.filter(groups__name__in = ['Administrador', 'Empleado']).distinct()

    else:
        trabajadores = Usuario.objects.filter(groups__name = 'Empleado')

    return render(request, 'usuarios/trabajador/ver_trabajadores.html', {'trabajadores': trabajadores})

#Editar trabajador
@administrador_required
def editar_trabajador(request, id):

    if request.user.is_superuser:
        trabajador = get_object_or_404(
            Usuario,
            id=id,
            groups__name__in=['Administrador', 'Empleado']
        )

    else:
        trabajador = get_object_or_404(
            Usuario,
            id=id,
            groups__name='Empleado'
        )

    if request.method == 'POST':

        formulario = EditarTrabajadorForm(
            request.POST,
            instance=trabajador
        )
        if not request.user.is_superuser:
            formulario.fields['grupo'].choices = [
                ('Empleado', 'Empleado')
            ]

        if formulario.is_valid():

            trabajador = formulario.save()

            grupo_seleccionado = formulario.cleaned_data['grupo']
            grupo = Group.objects.get(name=grupo_seleccionado)

            trabajador.groups.clear()
            trabajador.groups.add(grupo)

            return redirect('ver_trabajadores')

    else:

        grupo_actual = trabajador.groups.first()

        formulario = EditarTrabajadorForm(
            instance=trabajador,
            initial={
                'grupo': grupo_actual.name if grupo_actual else ''
            }
        )
        if not request.user.is_superuser:
            formulario.fields['grupo'].choices = [
                ('Empleado', 'Empleado')
            ]

    return render(request, 'usuarios/trabajador/editar_trabajador.html', {'formulario': formulario})

#Eliminar Trabajador
@administrador_required
def eliminar_trabajador(request, id):

    if request.user.is_superuser:
        trabajador = get_object_or_404(Usuario, id = id, groups__name__in=['Administrador', 'Empleado'])

    else:
        trabajador = get_object_or_404(Usuario, id = id, groups__name='Empleado')

    if request.method == 'POST':
        trabajador.delete()
        return redirect('ver_trabajadores')

    return render(request, 'usuarios/trabajador/eliminar_trabajador.html', {'trabajador': trabajador})

#FIN TRABAJADORES


#ver perfil
@login_required
def ver_perfil(request):

    usuario = request.user

    return render(request, 'usuarios/ver_perfil.html', {'usuario': usuario})

#Editar Perfil
@login_required
def editar_perfil(request):

    usuario = request.user

    if request.method == 'POST':

        formulario = EditarPerfilForm(request.POST, instance = usuario)

        if formulario.is_valid():
            formulario.save()
            return redirect('ver_perfil')

    else:

        formulario = EditarPerfilForm(instance = usuario) # Edito al usuario que tiene actualmente la sesión iniciada.

    return render(request, 'usuarios/editar_perfil.html', {'formulario': formulario})

#AUTENTICACION
#Iniciar Sesion
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

#Cerrar sesion
@login_required
def cerrar_sesion(request):

    if request.method == 'POST':
        logout(request)

    return redirect('inicio')