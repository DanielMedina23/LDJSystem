from django.urls import path
from . import views

urlpatterns = [
    path('', views.ver_reservas, name='ver_reservas'),
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('<int:pk>/', views.detalle_reserva, name='detalle_reserva'),
    path('<int:pk>/editar/', views.editar_reserva, name='editar_reserva'),
    path('<int:pk>/eliminar/', views.eliminar_reserva, name='eliminar_reserva'),
]