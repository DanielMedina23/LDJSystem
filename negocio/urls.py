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
]