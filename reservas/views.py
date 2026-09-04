from django.shortcuts import render, get_object_or_404, redirect
from .models import Reserva
from .forms import ReservaForm


    #Vista para crear una nueva reserva.
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save()
            return redirect('ver_reservas')
    else:
        form = ReservaForm()
        
    return render(request, 'reservas/crear_reserva.html', {'form': form})
#////////////////////////////////////////////////////////////////////////////////////////////

    #Vista para listar todas las reservas registradas.
def ver_reservas(request):
    reservas = Reserva.objects.all().order_by('-fecha_hora_inicio')
    return render(request, 'reservas/ver_reservas.html', {'reservas': reservas})
#////////////////////////////////////////////////////////////////////////////////////////////


    #Vista para ver el detalle de una reserva específica.
def detalle_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    return render(request, 'reservas/detalle_reserva.html', {'reserva': reserva})
#////////////////////////////////////////////////////////////////////////////////////////////


    #Vista para editar una reserva existente.
def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            return redirect('detalle_reserva', pk=reserva.pk)
    else:
        form = ReservaForm(instance=reserva)
        
    return render(request, 'reservas/editar_reserva.html', {
        'form': form,
        'reserva': reserva
    })
    #////////////////////////////////////////////////////////////////////////////////////////////

    #Vista para eliminar una reserva.
def eliminar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        reserva.delete()
        return redirect('ver_reservas')
        
    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})
