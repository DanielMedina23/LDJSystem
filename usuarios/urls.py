from django.urls import path
from .import views

urlpatterns = [
    path('agregar_cliente/', views.agregar_usuario, name = 'agregar_cliente'),
    path('login/',           views.iniciar_sesion, name = 'login'),
    path('inicio/',          views.inicio, name = 'inicio'),
    path('logout/', views.cerrar_sesion, name='logout'),
]