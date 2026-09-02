from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Negocio(models.Model):
    documento = models.CharField("Documento", max_length = 30, unique = True)
    nombre    = models.CharField("Nombre", max_length = 100)
    direccion = models.CharField("Direccion", max_length = 150)
    activo    = models.BooleanField("Activo", default = True)

    def __str__(self):
        return f"{self.nombre}"


class Mesa(models.Model):
    nombre_interno = models.CharField("Nombre", max_length = 20, unique = True)
    capacidad      = models.IntegerField("Capacidad", validators = [MinValueValidator(1)]) # Valido que la capacidad sea minimo 1
    activa         = models.BooleanField("Activa", default = True)

    def __str__(self):
        return f"{self.nombre_interno} - {self.capacidad}"

class Horario(models.Model):
    # Hago uso de Choices para dias semana para evitar errores al 
    # seleccionar los dias, en la siguiente lista el primer valor corresponde
    # a como se guarda el dato en la bd y el otro es la etiqueta como se va a mostrar el valor 
    DIAS_SEMANA = [
        ("lunes", "Lunes"),
        ("martes", "Martes"),
        ("miercoles", "Miercoles"),
        ("jueves", "Jueves"),
        ("viernes", "Viernes"),
        ("sabado", "Sabado"),
        ("domingo", "Domingo"),
    ]

    dia_semana    = models.CharField("Dia de la semana", max_length = 15, choices = DIAS_SEMANA)
    hora_apertura = models.TimeField("Apertura")
    hora_cierre   = models.TimeField("Cierre")

    def __str__(self):
        return 