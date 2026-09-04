from datetime import timedelta
from django.utils import timezone
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

    usuario_creador         = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True)
    mesa                    = models.ForeignKey(Mesa, on_delete = models.PROTECT, null = True, blank = True) 
    nombre_cliente          = models.CharField(max_length=150)
    telefono_cliente        = models.CharField(max_length=20, blank=True, null=True)
    correo_cliente          = models.EmailField(blank=True, null=True)
    fecha_hora_inicio       = models.DateTimeField()
    fecha_hora_fin          = models.DateTimeField(blank=True, null=True)
    num_personas            = models.IntegerField(validators=[MinValueValidator(1)])
    estado                  = models.CharField(max_length=30, choices=ESTADOS, default="pendiente_confirmacion")
    notas                   = models.TextField(blank=True, null=True)
    token_confirmacion      = models.CharField(max_length=100, blank=True, null=True)
    expiracion_confirmacion = models.DateTimeField(blank=True, null=True)
    
    # Si la fecha/hora de inicio está definida pero la de fin está vacía, calculamos 2 horas automáticamente
    def save(self, *args, **kwargs):
        if self.fecha_hora_inicio and not self.fecha_hora_fin:
            self.fecha_hora_fin = self.fecha_hora_inicio + timedelta(hours=2)
            
        super().save(*args, **kwargs)

     # Comprueba si la reserva está en curso y ya ha rebasado su hora de fin estimada
    def tiempo_expirado(self):
        if self.fecha_hora_fin and self.estado == 'en_curso':
            return timezone.now() > self.fecha_hora_fin
        return False

    def __str__(self):
        return f"Reserva {self.id} - {self.nombre_cliente} ({self.fecha_hora_inicio})"