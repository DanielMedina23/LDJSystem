from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Reserva
from .forms import ReservaForm


# Vista para crear una nueva reserva.
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            if request.user.is_authenticated:
                reserva.usuario_creador = request.user
            reserva.save()
            messages.success(request, f"¡La reserva #{reserva.id} se ha creado con éxito!")
            return redirect('ver_reservas')
    else:
        form = ReservaForm()
        
    return render(request, 'reservas/crear_reserva.html', {'form': form})

# ////////////////////////////////////////////////////////////////////////////////////////////

# Vista para listar todas las reservas registradas con soporte de filtros.
def ver_reservas(request):
    fecha_seleccionada = request.GET.get('fecha')
    estado_seleccionado = request.GET.get('estado')
    solo_expiradas = request.GET.get('expiradas')
    
    reservas = Reserva.objects.all().order_by('-fecha_hora_inicio')
    
    # 1. Filtro por fecha específica
    if fecha_seleccionada:
        reservas = reservas.filter(fecha_hora_inicio__date=fecha_seleccionada)
        
    # 2. Filtro por estado
    if estado_seleccionado:
        reservas = reservas.filter(estado=estado_seleccionado)
        
    # 3. Filtro de sobremesas expiradas basado en la propiedad del modelo
    if solo_expiradas:
        reservas = [r for r in reservas if r.es_expirada]

    return render(request, 'reservas/ver_reservas.html', {
        'reservas': reservas,
        'fecha_seleccionada': fecha_seleccionada,
        'estado_seleccionado': estado_seleccionado,
        'estados': Reserva.ESTADOS,
        'solo_expiradas': solo_expiradas,
    })
        
# ////////////////////////////////////////////////////////////////////////////////////////////

# Vista para ver el detalle de una reserva específica.
def detalle_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    return render(request, 'reservas/detalle_reserva.html', {'reserva': reserva})

# ////////////////////////////////////////////////////////////////////////////////////////////

# Vista para editar una reserva existente.
def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            reserva_obj = form.save(commit=False)
            nuevo_estado = request.POST.get('estado')
            if nuevo_estado in dict(Reserva.ESTADOS):
                reserva_obj.estado = nuevo_estado
            reserva_obj.save()
            messages.success(request, f"¡La reserva #{reserva_obj.id} se ha actualizado correctamente!")
            return redirect('detalle_reserva', pk=reserva_obj.pk)
    else:
        form = ReservaForm(instance=reserva)
        
    return render(request, 'reservas/editar_reserva.html', {
        'form': form,
        'reserva': reserva
    })
    
# ////////////////////////////////////////////////////////////////////////////////////////////

# Vista para eliminar una reserva.
def eliminar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        reserva_id = reserva.id
        reserva.delete()
        messages.success(request, f"¡La reserva #{reserva_id} ha sido eliminada con éxito!")
        return redirect('ver_reservas')
        
    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})

# ////////////////////////////////////////////////////////////////////////////////////////////

# Vista para cambiar el estado de una reserva a 'confirmada' de forma manual.
def confirmar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        reserva.estado = 'confirmada'
        reserva.save()
        messages.success(request, f"¡La reserva #{reserva.id} ha sido confirmada con éxito!")
        return redirect('ver_reservas')
    return redirect('ver_reservas')

# ////////////////////////////////////////////////////////////////////////////////////////////

# Vista para marcar una reserva como finalizada.
def finalizar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        reserva.estado = 'finalizada'
        reserva.save()
        messages.success(request, f"¡La reserva #{reserva.id} ha sido finalizada y guardada!")
        return redirect('ver_reservas')
        
    return render(request, 'reservas/finalizar_reserva.html', {'reserva': reserva})