from django.urls import path
from . import views

urlpatterns = [
    path('empleados/crear/', views.crear_empleado, name='crear_empleado'),

]