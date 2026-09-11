import os
import uuid
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

def crear_reserva(request):
    MesaBloqueo.purgar_expirados()

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    mesas = Mesa.objects.filter(
        activa=True
    ).order_by("id")

    bloqueos = {
        bloqueo.mesa_id: bloqueo.session_key
        for bloqueo in MesaBloqueo.objects.all()
    }

    estados_ocupantes = [
        'activa',
        'pendiente_confirmacion',
        'pendiente_revision',
        'confirmada',
        'en_curso',
    ]

    for mesa in mesas:
        if mesa.id in bloqueos:
            mesa.estado_visual = (
                "seleccionada"
                if bloqueos[mesa.id] == session_key
                else "ocupada"
            )

        else:
            tiene_reserva = Reserva.objects.filter(
                mesa_id=mesa.id,
                estado__in=estados_ocupantes
            ).exists()

            mesa.estado_visual = (
                "ocupada"
                if tiene_reserva
                else "libre"
            )

    reserva = None

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        mesa_id = request.POST.get('mesa')

        if not mesa_id:
            messages.error(
                request,
                "Por favor, selecciona una mesa en el plano."
            )

        elif form.is_valid():

            num_personas = form.cleaned_data['num_personas']
            fecha_hora_inicio = form.cleaned_data['fecha_hora_inicio']
            fecha_hora_fin = fecha_hora_inicio + timedelta(hours=2)

            estados_bloqueantes = [
                'activa',
                'pendiente_confirmacion',
                'pendiente_revision',
                'confirmada',
                'en_curso',
            ]

            with transaction.atomic():

                # Bloqueamos la mesa mientras comprobamos su disponibilidad
                mesa_seleccionada = Mesa.objects.select_for_update().filter(
                    id=mesa_id,
                    activa=True
                ).first()

                if mesa_seleccionada is None:
                    form.add_error(
                        None,
                        "La mesa seleccionada no existe o no está activa."
                    )

                elif mesa_seleccionada.capacidad < num_personas:
                    form.add_error(
                        None,
                        "La mesa seleccionada no tiene capacidad suficiente."
                    )

                else:
                    # Comprobamos otra vez que la mesa siga disponible
                    existe_solapamiento = Reserva.objects.filter(
                        mesa=mesa_seleccionada,
                        estado__in=estados_bloqueantes,
                        fecha_hora_inicio__lt=fecha_hora_fin,
                        fecha_hora_fin__gt=fecha_hora_inicio
                    ).exists()

                    if existe_solapamiento:
                        form.add_error(
                            None,
                            "La mesa seleccionada ya no está disponible para ese horario."
                        )

                    else:
                        reserva = form.save(commit=False)

                        reserva.mesa = mesa_seleccionada

                        if request.user.is_authenticated:
                            reserva.usuario_creador = request.user

                        reserva.token_confirmacion = uuid.uuid4().hex

                        reserva.expiracion_confirmacion = (
                            timezone.now() + timedelta(hours=24)
                        )

                        reserva.estado = 'activa'

                        reserva.save()

                        MesaBloqueo.objects.filter(
                            mesa_id=mesa_id
                        ).delete()

            if reserva and reserva.correo_cliente:
                link_relativo = reverse(
                    'confirmar_reserva_por_token',
                    kwargs={
                        'token': reserva.token_confirmacion
                    }
                )

                link_absoluto = request.build_absolute_uri(
                    link_relativo
                )

                asunto = (
                    f"Confirma tu reserva #{reserva.id} - LDJSystem"
                )

                mensaje = (
                    f"Hola {reserva.nombre_cliente},\n\n"
                    f"Gracias por realizar tu reserva para el "
                    f"{reserva.fecha_hora_inicio.strftime('%d/%m/%Y a las %H:%M')}.\n\n"
                    f"Por favor, confirma tu asistencia haciendo clic "
                    f"en el siguiente enlace:\n"
                    f"{link_absoluto}\n\n"
                    f"Este enlace caduca en 24 horas."
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

            if reserva:
                messages.success(
                    request,
                    f"¡La reserva #{reserva.id} se ha creado con éxito!"
                )

                return redirect('ver_reservas')

    else:
        form = ReservaForm()

    return render(
        request,
        'reservas/crear_reserva.html',
        {
            'form': form,
            'mesas': mesas
        }
    )

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

@personal_required
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

@personal_required
def detalle_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    return render(request, 'reservas/detalle_reserva.html', {'reserva': reserva})

@personal_required
def editar_reserva(request, pk):    
    """
    Permite al personal modificar una reserva existente.

    Busca la reserva que se quiere editar y procesa los nuevos datos
    enviados desde el formulario.

    Antes de guardar los cambios, comprueba que la mesa tenga capacidad
    suficiente y que no exista otra reserva en el mismo horario.
    La reserva que se está editando se excluye de esta comprobación
    para evitar que genere conflicto consigo misma.

    Si cambia la hora de inicio, también se vuelve a calcular la hora
    de finalización teniendo en cuenta una duración de 2 horas.

    Si todas las validaciones son correctas, actualiza la reserva.
    """

    # Buscamos la reserva que se quiere modificar
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)

        if form.is_valid():
            mesa = form.cleaned_data['mesa']
            num_personas = form.cleaned_data['num_personas']
            fecha_hora_inicio = form.cleaned_data['fecha_hora_inicio']

            # Calculamos nuevamente la hora final de la reserva
            fecha_hora_fin = fecha_hora_inicio + timedelta(hours=2)

            # Estados que hacen que una mesa se considere ocupada
            estados_bloqueantes = [
                'activa',
                'pendiente_confirmacion',
                'pendiente_revision',
                'confirmada',
                'en_curso',
            ]

            with transaction.atomic():

                # Bloqueamos la mesa mientras comprobamos su disponibilidad
                # para evitar que dos reservas la ocupen al mismo tiempo
                mesa_bloqueada = Mesa.objects.select_for_update().get(
                    pk=mesa.pk
                )

                # Comprobamos que la mesa tenga espacio para las personas indicadas
                if mesa_bloqueada.capacidad < num_personas:
                    form.add_error(
                        'mesa',
                        'La mesa seleccionada no tiene capacidad suficiente.'
                    )

                else:
                    # Buscamos otra reserva que use la misma mesa
                    # y coincida con el nuevo horario
                    existe_solapamiento = Reserva.objects.filter(
                        mesa=mesa_bloqueada,
                        estado__in=estados_bloqueantes,
                        fecha_hora_inicio__lt=fecha_hora_fin,
                        fecha_hora_fin__gt=fecha_hora_inicio
                    ).exclude(
                        pk=reserva.pk
                    ).exists()

                    if existe_solapamiento:
                        form.add_error(
                            'mesa',
                            'La mesa seleccionada coincide en horarios con otra reserva existente.'
                        )

                    else:
                        reserva_obj = form.save(commit=False)

                        reserva_obj.mesa = mesa_bloqueada

                        # Actualizamos también la hora final
                        reserva_obj.fecha_hora_fin = fecha_hora_fin

                        # Comprobamos que el nuevo estado sea válido
                        nuevo_estado = request.POST.get('estado')

                        if nuevo_estado in dict(Reserva.ESTADOS):
                            reserva_obj.estado = nuevo_estado

                        reserva_obj.save()

                        messages.success(
                            request,
                            f"¡La reserva #{reserva_obj.id} se ha actualizado correctamente!"
                        )

                        return redirect(
                            'detalle_reserva',
                            pk=reserva_obj.pk
                        )

    else:
        # Si entramos por GET, mostramos los datos actuales de la reserva
        form = ReservaForm(instance=reserva)

    return render(
        request,
        'reservas/editar_reserva.html',
        {
            'form': form,
            'reserva': reserva
        }
    )

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
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        reserva.estado = 'confirmada'
        reserva.save()
        messages.success(request, f"¡La reserva #{reserva.id} ha sido confirmada con éxito!")
        return redirect('ver_reservas')
    return redirect('ver_reservas')

@personal_required
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

@require_GET
def disponibilidad_mesas(request):
    """
        Busca las mesas disponibles para una fecha, hora y cantidad de personas.

        Primero valida los datos recibidos y calcula la hora de finalización
        de la reserva. Luego busca las mesas que tengan capacidad suficiente
        y comprueba que no tengan otra reserva en el mismo horario.

        Si se está editando una reserva, se ignora esa misma reserva para
        que no genere conflicto consigo misma.

        Devuelve los ID de las mesas que están disponibles.
    """

    fecha = request.GET.get("fecha_hora_inicio")
    num_personas = request.GET.get("num_personas")
    reserva_id = request.GET.get("reserva_id")

    try:
        num_personas = int(num_personas)

    except (TypeError, ValueError):
        return JsonResponse(
            {
                "ok": False,
                "error": "Número de personas inválido."
            },
            status=400
        )

    inicio = parse_datetime(fecha) if fecha else None

    if inicio is None:
        return JsonResponse(
            {
                "ok": False,
                "error": "Fecha/hora inválida."
            },
            status=400
        )

    if timezone.is_naive(inicio):
        inicio = timezone.make_aware(inicio)

    # Calculamos cuándo terminaría la reserva
    fin = inicio + timedelta(hours=2)

    # Buscamos mesas activas que tengan capacidad suficiente
    mesas = Mesa.objects.filter(activa=True, capacidad__gte=num_personas).order_by("id")

    # Estados de una reserva que hacen que la mesa no esté disponible
    estados_bloqueantes = [
        'activa',
        'pendiente_confirmacion',
        'pendiente_revision',
        'confirmada',
        'en_curso',
    ]

    disponibles = []

    for mesa in mesas:
        reservas_solapadas  = Reserva.objects.filter(
            mesa=mesa,
            estado__in=estados_bloqueantes,
            fecha_hora_inicio__lt=fin,
            fecha_hora_fin__gt=inicio,
        )

        # Si estamos editando, ignoramos la reserva actual
        # para que no entre en conflicto consigo misma
        if reserva_id:
            reservas_solapadas = reservas_solapadas.exclude(pk=reserva_id)

        ocupada = reservas_solapadas.exists()

        if not ocupada:
            disponibles.append(mesa.id)

    return JsonResponse({
        "ok": True,
        "mesas_disponibles": disponibles
    })
