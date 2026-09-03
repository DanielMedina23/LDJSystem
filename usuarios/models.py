from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    dni = models.CharField(max_length=9, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, unique=True)

    def __str__(self):
        return self.username
