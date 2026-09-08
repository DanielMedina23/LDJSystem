import os
import uuid
from datetime import timedelta
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from .forms import ReservaForm
from .models import Reserva
from django.conf import settings


def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            if request.user.is_authenticated:
                reserva.usuario_creador = request.user
            
            reserva.token_confirmacion = uuid.uuid4().hex
            reserva.expiracion_confirmacion = timezone.now() + timedelta(hours=24)
            reserva.save()

            if reserva.correo_cliente:
                link_relativo = reverse('confirmar_reserva_por_token', kwargs={'token': reserva.token_confirmacion})
                link_absoluto = request.build_absolute_uri(link_relativo)
                
                asunto = f"Confirma tu reserva #{reserva.id} - LDJSystem"
                mensaje = (
                    f"Hola {reserva.nombre_cliente},\n\n"
                    f"Gracias por realizar tu reserva para el {reserva.fecha_hora_inicio.strftime('%d/%m/%Y a las %H:%M')}.\n\n"
                    f"Por favor, confirma tu asistencia haciendo clic en el siguiente enlace:\n"
                    f"{link_absoluto}\n\n"
                    f"Este enlace caduca en 24 horas."
                )
                
                # Quitamos el try...except temporalmente para que si hay algún fallo, 
                # se muestre directamente en tu consola de Django y sepas qué ocurre.
                send_mail(
                    asunto, 
                    mensaje, 
                    os.getenv("EMAIL_HOST_USER"), 
                    [reserva.correo_cliente], 
                    fail_silently=False
                )

            messages.success(request, f"¡La reserva #{reserva.id} se ha creado con éxito!")
            return redirect('ver_reservas')
    else:
        form = ReservaForm()
        
    return render(request, 'reservas/crear_reserva.html', {'form': form})


def confirmar_reserva_por_token(request, token):
    reserva = get_object_or_404(Reserva, token_confirmacion=token)
    
    if reserva.expiracion_confirmacion and timezone.now() > reserva.expiracion_confirmacion:
        return render(request, 'reservas/confirmacion_resultado.html', {
            'exito': False,
            'mensaje': 'El enlace de confirmacion ha caducado. Por favor, ponte en contacto con nosotros.'
        })

    reserva.estado = 'confirmada'
    reserva.save()
    
    return render(request, 'reservas/confirmacion_resultado.html', {
        'exito': True,
        'reserva': reserva,
        'mensaje': f'¡Gracias {reserva.nombre_cliente}! Tu reserva ha sido confirmada con éxito.'
    })


def ver_reservas(request):
    fecha_seleccionada = request.GET.get('fecha')
    estado_seleccionado = request.GET.get('estado')
    solo_expiradas = request.GET.get('expiradas')
    q = request.GET.get('q', '').strip()
    
    reservas = Reserva.objects.all().order_by('-fecha_hora_inicio')
    
    if q:
        reservas = reservas.filter(
            Q(nombre_cliente__icontains=q) | 
            Q(telefono_cliente__icontains=q) | 
            Q(id__icontains=q)
        )

    if fecha_seleccionada:
        reservas = reservas.filter(fecha_hora_inicio__date=fecha_seleccionada)
        
    if estado_seleccionado:
        reservas = reservas.filter(estado=estado_seleccionado)
        
    if solo_expiradas:
        reservas = [r for r in reservas if r.es_expirada]

    total_reservas = len(reservas) if isinstance(reservas, list) else reservas.count()

    return render(request, 'reservas/ver_reservas.html', {
        'reservas': reservas,
        'fecha_seleccionada': fecha_seleccionada,
        'estado_seleccionado': estado_seleccionado,
        'estados': Reserva.ESTADOS,
        'solo_expiradas': solo_expiradas,
        'q': q,
        'total_reservas': total_reservas,
    })


def detalle_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    return render(request, 'reservas/detalle_reserva.html', {'reserva': reserva})


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


def eliminar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        reserva_id = reserva.id
        reserva.delete()
        messages.success(request, f"¡La reserva #{reserva_id} ha sido eliminada con éxito!")
        return redirect('ver_reservas')
        
    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})


def confirmar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        reserva.estado = 'confirmada'
        reserva.save()
        messages.success(request, f"¡La reserva #{reserva.id} ha sido confirmada con éxito!")
        return redirect('ver_reservas')
    return redirect('ver_reservas')


def finalizar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        reserva.estado = 'finalizada'
        reserva.save()
        
        if reserva.correo_cliente:
            asunto = f"¡Gracias por visitarnos, {reserva.nombre_cliente}!"
            mensaje = (
                f"Hola {reserva.nombre_cliente},\n\n"
                f"Esperamos que tu estancia en el bar haya sido de tu agrado.\n\n"
                f"¿Podrías valorarnos en nuestro perfil de Google? Nos ayudaría muchísimo a seguir mejorando:\n"
                f"{settings.GOOGLE_MAPS_REVIEW_URL}\n\n"
                f"¡Te esperamos pronto!"
            )
            try:
                send_mail(
                    asunto,
                    mensaje,
                    os.getenv("EMAIL_HOST_USER"),
                    [reserva.correo_cliente],
                    fail_silently=False
                )
            except Exception:
                pass

        messages.success(request, f"¡La reserva #{reserva.id} ha sido finalizada y se ha enviado la solicitud de reseña!")
        return redirect('ver_reservas')
        
    return render(request, 'reservas/finalizar_reserva.html', {'reserva': reserva})