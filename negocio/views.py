from django.shortcuts import render, redirect, get_object_or_404
from .models import Negocio, Mesa, Horario
from .forms import NegocioForm, MesaForm, HorarioForm

# vista para negocio


def ver_negocio(request):
    negocio = Negocio.objects.first()

    return render(
        request,
        'negocio/negocio.html',
        {'negocio': negocio}
    )

def crear_negocio(request):

    if request.method == 'POST':

        negocio_form = NegocioForm(request.POST)

        if negocio_form.is_valid():
            negocio_form.save()

            return redirect('ver_negocio')
    else:
        negocio_form = NegocioForm()

    return render(
        request,
        'negocio/crear.html',
        {'negocio_form': negocio_form}
    )


def editar_negocio(request, id):

    negocio = get_object_or_404(Negocio, id=id)

    if request.method == 'POST':

        negocio_form = NegocioForm(
            request.POST,
            instance=negocio
        )

        if negocio_form.is_valid():
            negocio_form.save()

            return redirect('ver_negocio')

    else:
        negocio_form = NegocioForm(instance=negocio)

    return render(
        request,
        'negocio/editar.html',
        {'negocio_form': negocio_form}
    )

def eliminar_negocio(request, id):

    negocio = get_object_or_404(Negocio, id=id)

    if request.method == 'POST':

        negocio.delete()

        return redirect('crear_negocio')

    return render(
        request,
        'negocio/eliminar.html',
        {'negocio': negocio}
    )

# vista para mesa
def crear_mesa(request):
    form = MesaForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("ver_mesas")

    return render(request, "mesa/crear.html", {"form": form})


def ver_mesas(request):
    mesas = Mesa.objects.all()

    return render(request, "mesa/mesa.html", {"mesas": mesas})


def editar_mesa(request, id):
    mesa = get_object_or_404(Mesa, id=id)

    form = MesaForm(request.POST or None, instance=mesa)

    if form.is_valid():
        form.save()
        return redirect("ver_mesas")

    return render(request, "mesa/editar.html", {"form": form})


def eliminar_mesa(request, id):

    mesa = get_object_or_404(Mesa, id=id)

    if request.method == 'POST':

        mesa.delete()

        return redirect('ver_mesas')

    return render(
        request,
        'mesa/eliminar.html',
        {'mesa': mesa}
    )


# Vista para Horarios

def ver_horarios(request):

    horarios = Horario.objects.all()

    return render(
        request,
        'horario/horario.html',
        {'horarios': horarios}
    )


def crear_horario(request):

    if request.method == 'POST':

        horario_form = HorarioForm(request.POST)

        if horario_form.is_valid():
            horario_form.save()

            return redirect('ver_horarios')

    else:

        horario_form = HorarioForm()

    return render(
        request,
        'horario/crear.html',
        {'horario_form': horario_form}
    )


def editar_horario(request, id):

    horario = get_object_or_404(Horario, id=id)

    if request.method == 'POST':

        horario_form = HorarioForm(
            request.POST,
            instance=horario
        )

        if horario_form.is_valid():
            horario_form.save()

            return redirect('ver_horarios')

    else:

        horario_form = HorarioForm(instance=horario)

    return render(
        request,
        'horario/editar.html',
        {'horario_form': horario_form}
    )


def eliminar_horario(request, id):

    horario = get_object_or_404(Horario, id=id)

    if request.method == 'POST':

        horario.delete()

        return redirect('ver_horarios')

    return render(
        request,
        'horario/eliminar.html',
        {'horario': horario}
    )
