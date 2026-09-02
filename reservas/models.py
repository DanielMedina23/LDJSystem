from django.db import models
from django.core.validators import MinValueValidator

from usuarios.models import Usuario
from negocio.models import Mesa

# Create your models here.
class Reserva(models.Model):

    ESTADOS = [
        ("pendiente_confirmacion", "Pendiente de confirmación"),
        ("pendiente_revision", "Pendiente de revisión"),
        ("confirmada", "Confirmada"),
        ("en_curso", "En curso"),
        ("finalizada", "Finalizada"),
        ("cancelada", "Cancelada"),
        ("rechazada", "Rechazada"),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True)
    mesa    = models.ForeignKey(Mesa, on_delete = models.PROTECT, null = True, blank = True) 
    nombre_invitado = models.CharField(max_length=150, blank=True, null=True)
    telefono_invitado = models.CharField(max_length=20, blank=True, null=True)
    correo_invitado = models.EmailField(blank=True, null=True)
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField(blank=True, null=True)
    num_personas = models.IntegerField(validators=[MinValueValidator(1)])
    estado = models.CharField(max_length=30, choices=ESTADOS)
    notas = models.TextField(blank=True, null=True)
    token_confirmacion = models.CharField(max_length=100, blank=True, null=True)
    expiracion_confirmacion = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Reserva {self.id} - {self.fecha_hora_inicio}"