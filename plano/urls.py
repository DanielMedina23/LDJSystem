from django.urls import path
from . import views

app_name = 'plano'

urlpatterns = [
    path('', views.ver_plano, name='ver_plano'),
    path('bloquear/', views.bloquear_mesa_temporal, name='bloquear_mesa_temporal'),
    path('actualizar-posicion/', views.actualizar_posicion_mesa, name='actualizar_posicion_mesa'),
    path('crear-reserva/', views.crear_reserva, name='crear_reserva'),
    path('liberar-bloqueo/', views.liberar_bloqueo_temporal, name='liberar_bloqueo_temporal'),
    path('detalle-reserva/', views.obtener_detalle_reserva, name='obtener_detalle_reserva'),
    path('liberar-ocupada/', views.liberar_mesa_ocupada, name='liberar_mesa_ocupada'),
    path('estado-mesas/', views.obtener_estado_mesas, name='estado_mesas'),
]