from django.urls import path
from .import views

urlpatterns = [
    #CLIENTES
    path('agregar_cliente/', views.agregar_usuario, name = 'agregar_cliente'),

    #TRABAJADOR
    path('crear_trabajador/',               views.crear_trabajador, name = 'crear_trabajador'),
    path('trabajadores/',                   views.ver_trabajadores, name = 'ver_trabajadores'),
    path('editar_trabajador/<int:id>/',     views.editar_trabajador, name = 'editar_trabajador'),
    path('trabajadores/eliminar/<int:id>/', views.eliminar_trabajador, name = 'eliminar_trabajador'),

    #RUTAS GENERALES DE USUARIO
    path('login/',         views.iniciar_sesion, name = 'login'),
    path('logout/',        views.cerrar_sesion, name = 'logout'),
    path('perfil/',        views.ver_perfil, name = 'ver_perfil'),
    path('perfil/editar/', views.editar_perfil, name = 'editar_perfil'),
]