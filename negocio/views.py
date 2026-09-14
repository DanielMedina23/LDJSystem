from django.shortcuts import render, redirect, get_object_or_404
from usuarios.decorators import personal_required
from .models import Negocio, Mesa, Horario
from .forms import NegocioForm, MesaForm, HorarioForm
from django.db.models import ProtectedError
from django.contrib import messages


# ==================================================
# GESTIÓN DE NEGOCIO
# ==================================================

@personal_required
def ver_negocio(request):
    negocio = Negocio.objects.first()
    return render(request, 'negocio/ver_negocio.html', {'negocio': negocio})


@personal_required
def crear_negocio(request):
    if request.method == 'POST':
        negocio_form = NegocioForm(request.POST)
        if negocio_form.is_valid():
            negocio_form.save()
            return redirect('ver_negocio')
    else:
        negocio_form = NegocioForm()

    return render(request, 'negocio/crear_negocio.html', {'negocio_form': negocio_form})


@personal_required
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


@personal_required
def eliminar_negocio(request, id):
    negocio = get_object_or_404(Negocio, id=id)
    if request.method == 'POST':
        negocio.delete()
        return redirect('crear_negocio')

    return render(request, 'negocio/eliminar_negocio.html', {'negocio': negocio})


# ==================================================
# GESTIÓN DE MESAS
# ==================================================

@personal_required
def crear_mesa(request):
    form = MesaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("ver_mesas")

    return render(request, "mesa/crear_mesa.html", {"form": form})


@personal_required
def ver_mesas(request):
    mesas = Mesa.objects.all().order_by("id")
    return render(request, "mesa/ver_mesas.html", {"mesas": mesas})


@personal_required
def editar_mesa(request, id):
    mesa = get_object_or_404(Mesa, id=id)
    form = MesaForm(request.POST or None, instance=mesa)
    if form.is_valid():
        form.save()
        return redirect("ver_mesas")

    return render(request, "mesa/editar_mesa.html", {"form": form})


@personal_required
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
# GESTIÓN DE HORARIOS
# ==================================================

@personal_required
def ver_horarios(request):
    horarios = Horario.objects.all().order_by("id")
    return render(request, 'negocio/ver_horarios.html', {'horarios': horarios})


@personal_required
def crear_horario(request):
    form = HorarioForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('ver_horarios')

    return render(request, 'negocio/crear_horario.html', {'form': form})


@personal_required
def editar_horario(request, id):
    horario = get_object_or_404(Horario, id=id)
    form = HorarioForm(request.POST or None, instance=horario)
    if form.is_valid():
        form.save()
        return redirect('ver_horarios')

    return render(request, 'negocio/editar_horario.html', {'form': form})


@personal_required
def eliminar_horario(request, id):
    horario = get_object_or_404(Horario, id=id)
    if request.method == 'POST':
        horario.delete()
        return redirect('ver_horarios')

    return render(request, 'negocio/eliminar_horario.html', {'horario': horario})