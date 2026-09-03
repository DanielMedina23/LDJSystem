from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # 1. Importamos TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='inicio.html'), name='inicio'),
    
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('negocio/', include('negocio.urls')),
    path('reservas/', include('reservas.urls')),
]