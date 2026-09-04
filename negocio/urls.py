from django.urls import path
from .import views


urlpatterns = [
    path('ver_negocio/', views.ver_negocio, name='ver_negocio'),

    path(
        'crear_negocio/',
        views.crear_negocio,
        name='crear_negocio'
    ),
    
    path(
        'editar_negocio/<int:id>/',
        views.editar_negocio,
        name='editar_negocio'
    ),

    path(
        'eliminar_negocio/<int:id>/',
        views.eliminar_negocio,
        name='eliminar_negocio'
    ),

#mesas

    path(
         'ver_mesas/', views.ver_mesas, name='ver_mesas'),

    path(
        'crear_mesa/',
        views.crear_mesa,
        name='crear_mesa'
    ),

    path(
        'editar_mesa/<int:id>/',
        views.editar_mesa,
        name='editar_mesa'
    ),

    path(
        'eliminar_mesa/<int:id>/',
        views.eliminar_mesa,
        name='eliminar_mesa'
    ),

#Horario

    path(
         'ver_horarios/', views.ver_horarios, name='ver_horarios'),

    path(
        'crear_horario/',
        views.crear_horario,
        name='crear_horario'
    ),

    path(
        'editar_horario/<int:id>/',
        views.editar_horario,
        name='editar_horario'
    ),

    path(
        'eliminar_horario/<int:id>/',
        views.eliminar_horario,
        name='eliminar_horario'
    ),



]