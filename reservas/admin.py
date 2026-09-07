from django.contrib import admin
from .models import Reserva

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'nombre_cliente', 
        'telefono_cliente', 
        'fecha_hora_inicio', 
        'fecha_hora_fin', 
        'num_personas', 
        'estado'
    )
    list_filter = ('estado', 'fecha_hora_inicio')
    search_fields = ('nombre_cliente', 'telefono_cliente', 'correo_cliente')
    readonly_fields = ('fecha_hora_fin', 'token_confirmacion', 'expiracion_confirmacion')