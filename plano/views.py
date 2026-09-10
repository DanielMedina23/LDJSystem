from datetime import timedelta
import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from negocio.models import Mesa
from reservas.models import Reserva
from .models import MesaBloqueo

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

def ver_plano(request):
    MesaBloqueo.purgar_expirados()
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    mesas = Mesa.objects.filter(activa=True).order_by("id")
    bloqueos = {b.mesa_id: b.session_key for b in MesaBloqueo.objects.all()}
    
    for mesa in mesas:
        if mesa.id in bloqueos:
            mesa.estado_visual = "seleccionada" if bloqueos[mesa.id] == session_key else "ocupada"
        else:
            mesa.estado_visual = "libre"

    return render(request, "plano/index.html", {"mesas": mesas})

@require_POST
def actualizar_posicion_mesa(request):
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
    
    datos_mesas = []
    for mesa in mesas:
        estado = "libre"
        if mesa.id in bloqueos:
            estado = "seleccionada" if bloqueos[mesa.id] == session_key else "ocupada"
        else:
            tiene_reserva = Reserva.objects.filter(mesa_id=mesa.id, estado='activa').exists()
            if tiene_reserva:
                estado = "ocupada"
        datos_mesas.append({"id": mesa.id, "estado": estado})

    return JsonResponse({"ok": True, "mesas": datos_mesas})