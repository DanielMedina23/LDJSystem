from django.shortcuts import render, redirect, get_object_or_404
from .models import Negocio
from .forms import NegocioForm

# Create your views here.
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