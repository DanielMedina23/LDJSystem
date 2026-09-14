import os
import uuid
import threading
import logging
from datetime import timedelta
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.dateparse import parse_datetime
from .forms import ReservaForm
from .models import Reserva
from negocio.models import Mesa
from plano.models import MesaBloqueo
from usuarios.decorators import personal_required
from django.core.management.base import BaseCommand
from django.utils import timezone
from reservas.models import Reserva

logger = logging.getLogger(__name__)

def enviar_correo_asincrono(asunto, mensaje, destinatario):
    """
    Ejecuta el envío de correos en un hilo secundario para evitar 
    bloquear la respuesta HTTP si el servidor SMTP presenta latencia.
    """
    try:
        send_mail(asunto, mensaje, os.getenv("EMAIL_HOST_USER"), [destinatario], fail_silently=False)
    except Exception as e:
        logger.error(f"CRÍTICO: Fallo al enviar correo a {destinatario}. Error: {str(e)}")


def crear_reserva(request):
    """
    Renderiza el plano interactivo y procesa la creación de nuevas reservas.
    Incluye protección contra condiciones de carrera mediante select_for_update.
    """
    MesaBloqueo.purgar_expirados()

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    mesas = Mesa.objects.filter(activa=True).order_by("id")
    bloqueos = {bloqueo.mesa_id: bloqueo.session_key for bloqueo in MesaBloqueo.objects.all()}

    estados_ocupantes = ['activa', 'pendiente_confirmacion', 'pendiente_revision', 'confirmada', 'en_curso']

    # OPTIMIZACIÓN RENDIMIENTO: Prevención de consultas N+1 en la renderización del plano.
    # Se extraen todos los IDs ocupados hoy en una sola consulta a PostgreSQL.
    hoy = timezone.now().date()
    mesas_ocupadas_ids = set(Reserva.objects.filter(
        estado__in=estados_ocupantes,
        fecha_hora_inicio__date__gte=hoy
    ).values_list('mesa_id', flat=True))

    for mesa in mesas:
        if mesa.id in bloqueos:
            mesa.estado_visual = "seleccionada" if bloqueos[mesa.id] == session_key else "ocupada"
        else:
            mesa.estado_visual = "ocupada" if mesa.id in mesas_ocupadas_ids else "libre"

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        mesa_id = request.POST.get('mesa')

        if not mesa_id:
            messages.error(request, "Por favor, selecciona una mesa en el plano.")
        elif form.is_valid():
            num_personas = form.cleaned_data['num_personas']
            fecha_hora_inicio = form.cleaned_data['fecha_hora_inicio']
            fecha_hora_fin = fecha_hora_inicio + timedelta(hours=2)

            with transaction.atomic():
                # BLOQUEO TRANSACCIONAL: Evita solapamientos si dos usuarios eligen la misma mesa al mismo milisegundo.
                mesa_seleccionada = Mesa.objects.select_for_update().filter(id=mesa_id, activa=True).first()

                if mesa_seleccionada is None:
                    form.add_error(None, "La mesa seleccionada no existe o no está activa.")
                elif mesa_seleccionada.capacidad < num_personas:
                    form.add_error(None, "La mesa seleccionada no tiene capacidad suficiente.")
                else:
                    existe_solapamiento = Reserva.objects.filter(
                        mesa=mesa_seleccionada,
                        estado__in=estados_ocupantes,
                        fecha_hora_inicio__lt=fecha_hora_fin,
                        fecha_hora_fin__gt=fecha_hora_inicio
                    ).exists()

                    if existe_solapamiento:
                        form.add_error(None, "La mesa seleccionada ya no está disponible para ese horario.")
                    else:
                        reserva = form.save(commit=False)
                        reserva.mesa = mesa_seleccionada
                        if request.user.is_authenticated:
                            reserva.usuario_creador = request.user
                            
                        reserva.token_confirmacion = uuid.uuid4().hex
                        reserva.expiracion_confirmacion = timezone.now() + timedelta(hours=24)
                        reserva.estado = 'activa'
                        reserva.save()
                        
                        MesaBloqueo.objects.filter(mesa_id=mesa_id).delete()

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
                            threading.Thread(target=enviar_correo_asincrono, args=(asunto, mensaje, reserva.correo_cliente)).start()

                        messages.success(
                            request, 
                            "Has realizado la reserva correctamente, para confirmarla te enviaremos un correo electrónico donde podrás asegurar tu mesa."
                        )
                        return redirect('inicio')
    else:
        form = ReservaForm()

    return render(request, 'reservas/crear_reserva.html', {'form': form, 'mesas': mesas})


def confirmar_reserva_por_token(request, token):
    """
    Confirma una reserva usando el enlace enviado al correo del cliente.
    Valida la caducidad del token y previene confirmaciones sobre reservas ya canceladas o finalizadas.
    """
    reserva = get_object_or_404(Reserva, token_confirmacion=token)

    if reserva.expiracion_confirmacion and timezone.now() > reserva.expiracion_confirmacion:
        return render(request, 'reservas/confirmacion_resultado.html', {
            'exito': False,
            'mensaje': 'El enlace de confirmación ha caducado. Por favor, ponte en contacto con nosotros.'
        })

    if reserva.estado == 'confirmada':
        return render(request, 'reservas/confirmacion_resultado.html', {
            'exito': True, 'reserva': reserva, 'mensaje': 'Esta reserva ya había sido confirmada anteriormente.'
        })

    estados_no_confirmables = ['cancelada', 'finalizada', 'rechazada']
    if reserva.estado in estados_no_confirmables:
        return render(request, 'reservas/confirmacion_resultado.html', {
            'exito': False, 'mensaje': 'Esta reserva ya no puede ser confirmada. Por favor, ponte en contacto con nosotros.'
        })

    reserva.estado = 'confirmada'
    reserva.save()

    return render(request, 'reservas/confirmacion_resultado.html', {
        'exito': True, 'reserva': reserva, 'mensaje': f'¡Gracias {reserva.nombre_cliente}! Tu reserva ha sido confirmada con éxito.'
    })


@personal_required
def ver_reservas(request):
    fecha_seleccionada = request.GET.get('fecha')
    estado_seleccionado = request.GET.get('estado')
    solo_expiradas = request.GET.get('expiradas')
    q = request.GET.get('q', '').strip()
    
    reservas = Reserva.objects.all().order_by('-fecha_hora_inicio')
    
    if q:
        reservas = reservas.filter(
            Q(nombre_cliente__icontains=q) | Q(telefono_cliente__icontains=q) | Q(id__icontains=q)
        )

    if fecha_seleccionada:
        reservas = reservas.filter(fecha_hora_inicio__date=fecha_seleccionada)
        
    if estado_seleccionado:
        reservas = reservas.filter(estado=estado_seleccionado)
        
    if solo_expiradas:
        # DELEGACIÓN A BASE DE DATOS: Prohibido cargar en RAM listas enteras para filtrar.
        reservas = reservas.filter(
            estado='activa', 
            expiracion_confirmacion__lt=timezone.now()
        )

    total_reservas = reservas.count()

    return render(request, 'reservas/ver_reservas.html', {
        'reservas': reservas,
        'fecha_seleccionada': fecha_seleccionada,
        'estado_seleccionado': estado_seleccionado,
        'estados': Reserva.ESTADOS,
        'solo_expiradas': solo_expiradas,
        'q': q,
        'total_reservas': total_reservas,
    })


@personal_required
def detalle_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    return render(request, 'reservas/detalle_reserva.html', {'reserva': reserva})


@personal_required
def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        
        if form.is_valid():
            # FALLBACK: Si el POST no trae mesa (ej. campo disabled en HTML), usamos la que ya existe en BD
            mesa = form.cleaned_data.get('mesa') or reserva.mesa
            num_personas = form.cleaned_data.get('num_personas', reserva.num_personas)
            fecha_hora_inicio = form.cleaned_data.get('fecha_hora_inicio', reserva.fecha_hora_inicio)
            fecha_hora_fin = fecha_hora_inicio + timedelta(hours=2)

            estados_bloqueantes = ['activa', 'pendiente_confirmacion', 'pendiente_revision', 'confirmada', 'en_curso']
            
            # Recuperamos el nuevo estado si el form lo permite, sino mantenemos el actual
            nuevo_estado = request.POST.get('estado', reserva.estado)

            # Preparamos el objeto sin impactar en BD
            reserva_obj = form.save(commit=False)
            reserva_obj.estado = nuevo_estado

            with transaction.atomic():
                # BYPASS LÓGICO: Si la reserva se cancela o finaliza, no comprobamos colisiones ni bloqueamos mesas.
                if nuevo_estado not in estados_bloqueantes:
                    reserva_obj.mesa = mesa
                    reserva_obj.fecha_hora_fin = fecha_hora_fin
                    reserva_obj.save()
                    messages.success(request, f"¡La reserva #{reserva_obj.id} se ha actualizado correctamente (Sin ocupar mesa)!")
                    return redirect('detalle_reserva', pk=reserva_obj.pk)

                # VALIDACIÓN ESTRICTA: Solo se ejecuta si la reserva va a ocupar físicamente una mesa
                mesa_bloqueada = Mesa.objects.select_for_update().get(pk=mesa.pk)

                if mesa_bloqueada.capacidad < num_personas:
                    form.add_error('mesa', 'La mesa seleccionada no tiene capacidad suficiente.')
                else:
                    existe_solapamiento = Reserva.objects.filter(
                        mesa=mesa_bloqueada,
                        estado__in=estados_bloqueantes,
                        fecha_hora_inicio__lt=fecha_hora_fin,
                        fecha_hora_fin__gt=fecha_hora_inicio
                    ).exclude(pk=reserva.pk).exists()

                    if existe_solapamiento:
                        form.add_error('mesa', 'La mesa seleccionada coincide en horarios con otra reserva existente.')
                    else:
                        reserva_obj.mesa = mesa_bloqueada
                        reserva_obj.fecha_hora_fin = fecha_hora_fin
                        reserva_obj.save()

                        messages.success(request, f"¡La reserva #{reserva_obj.id} se ha actualizado correctamente!")
                        return redirect('detalle_reserva', pk=reserva_obj.pk)
    else:
        form = ReservaForm(instance=reserva)

    mesas = Mesa.objects.filter(activa=True).order_by('id')
    return render(request, 'reservas/editar_reserva.html', {'form': form, 'reserva': reserva, 'mesas': mesas})


@personal_required
def eliminar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        reserva_id = reserva.id
        reserva.delete()
        messages.success(request, f"¡La reserva #{reserva_id} ha sido eliminada con éxito!")
        return redirect('ver_reservas')
        
    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})


@personal_required
def confirmar_reserva(request, pk):
    """
    Fuerza la confirmación manual de una reserva desde el dashboard del personal.
    """
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.method == 'POST':
        if reserva.estado == 'confirmada':
            messages.info(request, f"La reserva #{reserva.id} ya estaba confirmada.")
            return redirect('ver_reservas')

        estados_no_confirmables = ['cancelada', 'finalizada', 'rechazada']
        if reserva.estado in estados_no_confirmables:
            messages.error(request, f"La reserva #{reserva.id} ya no se puede confirmar.")
            return redirect('ver_reservas')

        reserva.estado = 'confirmada'
        reserva.save()
        messages.success(request, f"¡La reserva #{reserva.id} ha sido confirmada con éxito!")
        return redirect('ver_reservas')

    return redirect('ver_reservas')


@personal_required
def finalizar_reserva(request, pk):
    """
    Concluye el ciclo de vida de la reserva, liberando la mesa.
    Permite cerrar reservas activas, confirmadas o en curso sin exigir estados intermedios rígidos,
    activando de forma asíncrona el envío del correo de reseña si existe contacto.
    """
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.method == 'POST':
        estados_cerrables = ['activa', 'pendiente_confirmacion', 'confirmada', 'en_curso']
        
        if reserva.estado not in estados_cerrables:
            messages.error(request, "Esta reserva ya fue cancelada o finalizada previamente.")
            return redirect('detalle_reserva', pk=reserva.pk)

        reserva.estado = 'finalizada'
        reserva.save()

        if reserva.correo_cliente:
            asunto = f"¡Gracias por visitarnos, {reserva.nombre_cliente}!"
            mensaje = (
                f"Hola {reserva.nombre_cliente},\n\n"
                f"Esperamos que tu estancia en el bar haya sido de tu agrado.\n\n"
                f"¿Podrías valorarnos en nuestro perfil de Google? Nos ayudaría muchísimo a seguir mejorando:\n"
                f"{getattr(settings, 'GOOGLE_MAPS_REVIEW_URL', 'Enlace no configurado')}\n\n"
                f"¡Te esperamos pronto!"
            )
            threading.Thread(target=enviar_correo_asincrono, args=(asunto, mensaje, reserva.correo_cliente)).start()

        messages.success(request, f"¡La reserva #{reserva.id} ha sido finalizada correctamente!")
        return redirect('ver_reservas')

    return render(request, 'reservas/finalizar_reserva.html', {'reserva': reserva})


@require_GET
def disponibilidad_mesas(request):
    """
    Endpoint JSON que retorna las IDs de las mesas disponibles dada una fecha y número de comensales.
    Excluye la propia reserva si se está ejecutando desde el contexto de edición.
    """
    fecha = request.GET.get("fecha_hora_inicio")
    num_personas = request.GET.get("num_personas")
    reserva_id = request.GET.get("reserva_id")

    try:
        num_personas = int(num_personas)
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Número de personas inválido."}, status=400)

    inicio = parse_datetime(fecha) if fecha else None
    if inicio is None:
        return JsonResponse({"ok": False, "error": "Fecha/hora inválida."}, status=400)

    if timezone.is_naive(inicio):
        inicio = timezone.make_aware(inicio)

    fin = inicio + timedelta(hours=2)
    mesas = Mesa.objects.filter(activa=True, capacidad__gte=num_personas).order_by("id")
    estados_bloqueantes = ['activa', 'pendiente_confirmacion', 'pendiente_revision', 'confirmada', 'en_curso']

    # OPTIMIZACIÓN N+1: Obtenemos el conjunto de IDs ocupados en 1 consulta para iterar en memoria RAM O(1).
    reservas_solapadas = Reserva.objects.filter(
        estado__in=estados_bloqueantes,
        fecha_hora_inicio__lt=fin,
        fecha_hora_fin__gt=inicio
    )
    
    if reserva_id:
        reservas_solapadas = reservas_solapadas.exclude(pk=reserva_id)

    mesas_ocupadas_ids = set(reservas_solapadas.values_list('mesa_id', flat=True))
    disponibles = [mesa.id for mesa in mesas if mesa.id not in mesas_ocupadas_ids]

    return JsonResponse({"ok": True, "mesas_disponibles": disponibles})

