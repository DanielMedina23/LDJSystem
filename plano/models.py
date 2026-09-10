from django.db import models
from django.utils import timezone
from negocio.models import Mesa

class MesaBloqueo(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='bloqueos')
    session_key = models.CharField(max_length=40)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'plano_mesa_bloqueo'
        constraints = [
            models.UniqueConstraint(fields=['mesa'], name='unique_mesa_bloqueo')
        ]

    @classmethod
    def purgar_expirados(cls):
        """Elimina todos los bloqueos temporales cuyo tiempo haya vencido."""
        cls.objects.filter(expires_at__lte=timezone.now()).delete()

    def __str__(self):
        return f"Bloqueo Mesa {self.mesa.id} hasta {self.expires_at}"