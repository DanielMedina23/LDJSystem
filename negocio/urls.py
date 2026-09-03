from django.urls import path
from .import views


urlpatterns = [
    path('', views.ver_negocio, name='ver_negocio'),

    path(
        'crear/',
        views.crear_negocio,
        name='crear_negocio'
    ),

    path(
        'editar/<int:id>/',
        views.editar_negocio,
        name='editar_negocio'
    ),

    path(
        'eliminar/<int:id>/',
        views.eliminar_negocio,
        name='eliminar_negocio'
    ),

#mesas

    path(
         '', views.ver_mesas, name='ver_mesas'),

    path(
        'crear/',
        views.crear_mesa,
        name='crear_mesa'
    ),

    path(
        'editar/<int:id>/',
        views.editar_mesa,
        name='editar_mesa'
    ),

    path(
        'eliminar/<int:id>/',
        views.eliminar_mesa,
        name='eliminar_negocio'
    ),

#Horario

    path(
         '', views.ver_horarios, name='ver_horarios'),

    path(
        'crear/',
        views.crear_horario,
        name='crear_horario'
    ),

    path(
        'editar/<int:id>/',
        views.editar_mesa,
        name='editar_horario'
    ),

    path(
        'eliminar/<int:id>/',
        views.eliminar_mesa,
        name='eliminar_horario'
    ),



]