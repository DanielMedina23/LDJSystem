from datetime import timedelta
import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from negocio.models import Mesa
from reservas.models import Reserva
from .models import MesaBloqueo

def _es_jefe_o_trabajador(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name__in=['Jefes', 'Trabajadores']).exists()

def _es_jefe_o_superadmin(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='Jefes').exists()

@require_POST
def bloquear_mesa_temporal(request):
    try:
        datos = json.loads(request.body)
        mesa_id = int(datos.get("mesa_id"))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    mesa = get_object_or_404(Mesa, id=mesa_id, activa=True)
    
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    MesaBloqueo.purgar_expirados()

    bloqueo_existente = MesaBloqueo.objects.filter(mesa=mesa).first()
    if bloqueo_existente and bloqueo_existente.session_key != session_key:
        return JsonResponse({"ok": False, "error": "La mesa ya está ocupada o siendo seleccionada por otro usuario."}, status=409)

    expires_at = timezone.now() + timedelta(seconds=120)
    MesaBloqueo.objects.update_or_create(
        mesa=mesa,
        defaults={
            "session_key": session_key,
            "expires_at": expires_at
        }
    )

    return JsonResponse({"ok": True, "expires_at": expires_at.isoformat()})

@login_required(login_url='/usuarios/login/')
@user_passes_test(_es_jefe_o_trabajador, login_url='/usuarios/login/')
def ver_plano(request):
    MesaBloqueo.purgar_expirados()
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    mesas = Mesa.objects.filter(activa=True).order_by("id")
    bloqueos = {b.mesa_id: b.session_key for b in MesaBloqueo.objects.all()}
    
    ahora = timezone.now()
    estados_ocupantes = ['activa', 'pendiente_confirmacion', 'confirmada', 'en_curso']

    for mesa in mesas:
        if mesa.id in bloqueos:
            mesa.estado_visual = "seleccionada" if bloqueos[mesa.id] == session_key else "ocupada"
        else:
            tiene_reserva_vigente = Reserva.objects.filter(
                mesa_id=mesa.id,
                estado__in=estados_ocupantes,
                fecha_hora_inicio__lte=ahora,
                fecha_hora_fin__gte=ahora
            ).exists()
            mesa.estado_visual = "ocupada" if tiene_reserva_vigente else "libre"

    return render(request, "plano/ver_plano.html", {
        "mesas": mesas,
        "es_jefe_o_superadmin": _es_jefe_o_superadmin(request.user)
    })

@require_POST
def actualizar_posicion_mesa(request):
    if not _es_jefe_o_superadmin(request.user):
        return JsonResponse({"ok": False, "error": "No autorizado. Solo Jefes pueden modificar el plano."}, status=403)

    try:
        datos = json.loads(request.body)
        mesa_id = int(datos.get("mesa_id"))
        x = int(datos.get("x"))
        y = int(datos.get("y"))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa.x = x
    mesa.y = y
    mesa.save(update_fields=['x', 'y'])

    return JsonResponse({"ok": True})

@require_POST
def crear_mesa(request):
    if not _es_jefe_o_superadmin(request.user):
        return JsonResponse({"ok": False, "error": "No autorizado. Solo Jefes pueden añadir mesas."}, status=403)

    try:
        datos = json.loads(request.body)
        nombre = datos.get("nombre")
        capacidad = int(datos.get("capacidad"))
        x = int(datos.get("x", 100))
        y = int(datos.get("y", 100))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    mesa = Mesa.objects.create(
        nombre_interno=nombre, 
        capacidad=capacidad, 
        x=x, 
        y=y, 
        ancho=120, 
        alto=70, 
        forma='rectangulo', 
        activa=True
    )
    return JsonResponse({"ok": True, "mesa_id": mesa.id})

@require_POST
def modificar_mesa(request):
    if not _es_jefe_o_superadmin(request.user):
        return JsonResponse({"ok": False, "error": "No autorizado. Solo Jefes pueden modificar mesas."}, status=403)

    try:
        datos = json.loads(request.body)
        mesa_id = int(datos.get("mesa_id"))
        nombre = datos.get("nombre")
        capacidad = int(datos.get("capacidad"))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa.nombre_interno = nombre
    mesa.capacidad = capacidad
    mesa.save(update_fields=['nombre_interno', 'capacidad'])
    return JsonResponse({"ok": True})

@require_POST
def eliminar_mesa(request):
    if not _es_jefe_o_superadmin(request.user):
        return JsonResponse({"ok": False, "error": "No autorizado. Solo Jefes pueden eliminar mesas."}, status=403)

    try:
        datos = json.loads(request.body)
        mesa_id = int(datos.get("mesa_id"))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa.activa = False
    mesa.save(update_fields=['activa'])
    MesaBloqueo.objects.filter(mesa=mesa).delete()
    return JsonResponse({"ok": True})

@require_POST
def crear_reserva(request):
    try:
        datos = json.loads(request.body)
        mesa_id = int(datos.get("mesa_id"))
        cliente_nombre = datos.get("cliente")
        comensales = int(datos.get("comensales"))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    if comensales > mesa.capacidad:
        return JsonResponse({"ok": False, "error": f"La capacidad máxima de la mesa es {mesa.capacidad} comensales."}, status=400)

    with transaction.atomic():
        Reserva.objects.create(
            mesa=mesa, 
            cliente=cliente_nombre, 
            comensales=comensales, 
            estado='activa'
        )
        MesaBloqueo.objects.filter(mesa=mesa).delete()

    return JsonResponse({"ok": True})

@csrf_exempt
@require_POST
def liberar_bloqueo_temporal(request):
    try:
        datos = json.loads(request.body)
        mesa_id = int(datos.get("mesa_id"))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    session_key = request.session.session_key
    if session_key:
        MesaBloqueo.objects.filter(mesa_id=mesa_id, session_key=session_key).delete()

    return JsonResponse({"ok": True})

@require_POST
def obtener_detalle_reserva(request):
    try:
        datos = json.loads(request.body)
        mesa_id = int(datos.get("mesa_id"))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    reserva = Reserva.objects.filter(mesa_id=mesa_id, estado='activa').last()
    if not reserva:
        return JsonResponse({"ok": False, "error": "No hay información de reserva activa para esta mesa."}, status=404)

    return JsonResponse({
        "ok": True,
        "cliente": getattr(reserva, 'cliente', 'Desconocido'),
        "comensales": getattr(reserva, 'comensales', 0)
    })

@require_POST
def liberar_mesa_ocupada(request):
    if not _es_jefe_o_trabajador(request.user):
        return JsonResponse({"ok": False, "error": "No autorizado."}, status=403)

    try:
        datos = json.loads(request.body)
        mesa_id = int(datos.get("mesa_id"))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    Reserva.objects.filter(mesa_id=mesa_id, estado='activa').update(estado='cancelada')
    MesaBloqueo.objects.filter(mesa_id=mesa_id).delete()

    return JsonResponse({"ok": True})

@require_GET
def obtener_estado_mesas(request):
    MesaBloqueo.purgar_expirados()
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    mesas = Mesa.objects.filter(activa=True)
    bloqueos = {b.mesa_id: b.session_key for b in MesaBloqueo.objects.all()}
    
    ahora = timezone.now()
    estados_ocupantes = ['activa', 'pendiente_confirmacion', 'confirmada', 'en_curso']
    
    datos_mesas = []
    for mesa in mesas:
        estado = "libre"
        if mesa.id in bloqueos:
            estado = "seleccionada" if bloqueos[mesa.id] == session_key else "ocupada"
        else:
            tiene_reserva_vigente = Reserva.objects.filter(
                mesa_id=mesa.id,
                estado__in=estados_ocupantes,
                fecha_hora_inicio__lte=ahora,
                fecha_hora_fin__gte=ahora
            ).exists()
            
            if tiene_reserva_vigente:
                estado = "ocupada"
        datos_mesas.append({"id": mesa.id, "estado": estado})

    return JsonResponse({"ok": True, "mesas": datos_mesas})