from django.urls import path
from . import views

app_name = 'plano'

urlpatterns = [
    path('', views.ver_plano, name='ver_plano'),
    path('bloquear/', views.bloquear_mesa_temporal, name='bloquear_mesa_temporal'),
    path('liberar-bloqueo/', views.liberar_bloqueo_temporal, name='liberar_bloqueo_temporal'),
    path('actualizar-posicion/', views.actualizar_posicion_mesa, name='actualizar_posicion_mesa'),
    path('crear/', views.crear_mesa, name='crear_mesa'),
    path('modificar/', views.modificar_mesa, name='modificar_mesa'),
    path('eliminar/', views.eliminar_mesa, name='eliminar_mesa'),
    path('crear-reserva/', views.crear_reserva, name='crear_reserva'),
    path('detalle-reserva/', views.obtener_detalle_reserva, name='obtener_detalle_reserva'),
    path('liberar-mesa/', views.liberar_mesa_ocupada, name='liberar_mesa_ocupada'),
    path('estado-mesas/', views.obtener_estado_mesas, name='estado_mesas'),
]