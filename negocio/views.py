from django.shortcuts import render, redirect, get_object_or_404
from usuarios.decorators import personal_required, administrador_required
from .models import Negocio, Mesa, Horario
from .forms import NegocioForm, MesaForm, HorarioForm
from django.db.models import ProtectedError
from django.contrib import messages


# ==================================================
# GESTIÓN DE NEGOCIO (VISTA PÚBLICA / ADMIN)
# ==================================================

def ver_negocio(request):
    negocio = Negocio.objects.first()
    
    # Mapeamos para obtener solo el último o único horario por día de la semana
    horarios_dict = {}
    for h in Horario.objects.all():
        horarios_dict[h.dia_semana] = h
        
    dias_ordenados = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    horarios = [horarios_dict[dia] for dia in dias_ordenados if dia in horarios_dict]
    
    es_jefe = request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name='Jefes').exists())
    
    return render(request, 'negocio/ver_negocio.html', {
        'negocio': negocio,
        'horarios': horarios,
        'es_jefe': es_jefe
    })


@administrador_required
def crear_negocio(request):
    if request.method == 'POST':
        negocio_form = NegocioForm(request.POST)
        if negocio_form.is_valid():
            negocio_form.save()
            return redirect('ver_negocio')
    else:
        negocio_form = NegocioForm()

    return render(request, 'negocio/crear_negocio.html', {'negocio_form': negocio_form})


@administrador_required
def editar_negocio(request, id):
    negocio = get_object_or_404(Negocio, id=id)
    if request.method == 'POST':
        negocio_form = NegocioForm(request.POST, instance=negocio)
        if negocio_form.is_valid():
            negocio_form.save()
            return redirect('ver_negocio')
    else:
        negocio_form = NegocioForm(instance=negocio)

    return render(request, 'negocio/editar_negocio.html', {'negocio_form': negocio_form})


@administrador_required
def eliminar_negocio(request, id):
    negocio = get_object_or_404(Negocio, id=id)
    if request.method == 'POST':
        negocio.delete()
        return redirect('crear_negocio')

    return render(request, 'negocio/eliminar_negocio.html', {'negocio': negocio})


# ==================================================
# GESTIÓN DE MESAS
# ==================================================

@administrador_required
def crear_mesa(request):
    form = MesaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("ver_mesas")

    return render(request, "mesa/crear_mesa.html", {"form": form})


@administrador_required
def ver_mesas(request):
    mesas = Mesa.objects.all().order_by("id")
    return render(request, "mesa/ver_mesas.html", {"mesas": mesas})


@administrador_required
def editar_mesa(request, id):
    mesa = get_object_or_404(Mesa, id=id)
    form = MesaForm(request.POST or None, instance=mesa)
    if form.is_valid():
        form.save()
        return redirect("ver_mesas")

    return render(request, "mesa/editar_mesa.html", {"form": form})


@administrador_required
def eliminar_mesa(request, id):
    mesa = get_object_or_404(Mesa, id=id)
    
    if request.method == 'POST':
        try:
            mesa.delete()
            messages.success(request, "La mesa ha sido eliminada exitosamente.")
            return redirect('ver_mesas')
        except ProtectedError:
            messages.error(request, "No se puede eliminar esta mesa porque cuenta con reservas asociadas en el sistema.")
            return redirect('ver_mesas')

    return render(request, 'mesa/eliminar_mesa.html', {'mesa': mesa})


# ==================================================
# GESTIÓN DE HORARIOS (VISTA PÚBLICA / ADMIN)
# ==================================================

def ver_horarios(request):
    dias_ordenados = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    horarios_dict = {h.dia_semana: h for h in Horario.objects.all()}
    
    horarios_semana = []
    for dia_key in dias_ordenados:
        horario_obj = horarios_dict.get(dia_key)
        # Obtenemos la etiqueta legible del choices del modelo
        dia_display = dict(Horario.DIAS_SEMANA).get(dia_key)
        horarios_semana.append({
            'dia_key': dia_key,
            'dia_display': dia_display,
            'horario': horario_obj
        })

    return render(request, 'horario/ver_horarios.html', {'horarios_semana': horarios_semana})


@administrador_required
def crear_horario(request):
    form = HorarioForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('ver_horarios')

    return render(request, 'horario/crear_horario.html', {'form': form})


@administrador_required
def editar_horario(request, id):
    horario = get_object_or_404(Horario, id=id)
    form = HorarioForm(request.POST or None, instance=horario)
    if form.is_valid():
        form.save()
        return redirect('ver_horarios')

    return render(request, 'horario/editar_horario.html', {'form': form})


@administrador_required
def eliminar_horario(request, id):
    horario = get_object_or_404(Horario, id=id)
    if request.method == 'POST':
        horario.delete()
        return redirect('ver_horarios')

    return render(request, 'horario/eliminar_horario.html', {'horario': horario})