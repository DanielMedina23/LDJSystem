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
            grupo_cliente, _ = Group.objects.get_or_create(name='Cliente')

            # Agrego el usuario recién registrado al grupo Cliente
            usuario.groups.add(grupo_cliente)

            # Envio al cliente a la ventana principal
            return redirect('inicio')

    else:

        # Si entra por primera vez a la página,
        # creo un formulario vacío
        formulario = RegistroClienteForm()

    # Envío el formulario al template para poder mostrarlo
    return render(request, 'inicio.html', {'formulario' : formulario})
    # return render(request, 'usuarios/cliente/agregar_cliente.html', {'formulario': formulario})

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
            ('Trabajadores', 'Trabajador')
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
        trabajadores = Usuario.objects.filter(groups__name__in = ['Jefes', 'Trabajadores']).distinct()

    else:
        trabajadores = Usuario.objects.filter(groups__name = 'Trabajadores')

    return render(request, 'usuarios/trabajador/ver_trabajadores.html', {'trabajadores': trabajadores})

#Editar trabajador
@administrador_required
def editar_trabajador(request, id):

    trabajador = get_object_or_404(
        Usuario,
        id=id
    )

    if request.method == 'POST':

        formulario = EditarTrabajadorForm(
            request.POST,
            instance=trabajador
        )

        if not request.user.is_superuser:
            formulario.fields['grupo'].choices = [
                ('Trabajadores', 'Trabajadores')
            ]

        if formulario.is_valid():

            trabajador = formulario.save()

            grupo_seleccionado = formulario.cleaned_data['grupo']

            grupo = Group.objects.get(
                name=grupo_seleccionado
            )

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
                ('Trabajadores', 'Trabajadores')
            ]

    return render(
        request,
        'usuarios/trabajador/editar_trabajador.html',
        {
            'formulario': formulario,
            'trabajador': trabajador
        }
    )

#Eliminar Trabajador
@administrador_required
def eliminar_trabajador(request, id):

    trabajador = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        trabajador.delete()
        return redirect('ver_trabajadores')

    return render(
        request,
        'usuarios/trabajador/eliminar_trabajador.html',
        {'trabajador': trabajador}
    )

#FIN TRABAJADORES


#ver perfil
@login_required
def ver_perfil(request):

    usuario = request.user
    # Creamos el formulario con los datos actuales
    # del usuario que tiene la sesión iniciada.
    formulario = EditarPerfilForm(instance=usuario)

    return render(request, 'usuarios/ver_perfil.html', {'usuario': usuario,
                                                        'formulario' : formulario})

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

    return render(request, 'usuarios/ver_perfil.html', {'usuario' : usuario,
                                                        'formulario': formulario})

#AUTENTICACION
#Iniciar Sesion
def iniciar_sesion(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Capturamos el parámetro next inyectado por el decorador o el formulario ocuto
        next_url = request.POST.get('next') or request.GET.get('next')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            
            # Si hay una URL pendiente, redirigimos ahí para que el decorador evalúe el rol
            if next_url:
                return redirect(next_url)
                
            return redirect('inicio')
        else:
            error = 'Usuario o contraseña incorrectos'

    return render(request, 'usuarios/login.html', {'error': error})
#Cerrar sesion
@login_required
def cerrar_sesion(request):

    if request.method == 'POST':
        logout(request)

    return redirect('inicio')