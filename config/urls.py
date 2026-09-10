from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- RUTAS LEGALES ---
    path('aviso-legal/', TemplateView.as_view(template_name='legales/aviso_legal.html'), name='aviso_legal'),
    path('politica-privacidad/', TemplateView.as_view(template_name='legales/politica_privacidad.html'), name='politica_privacidad'),
    path('politica-cookies/', TemplateView.as_view(template_name='legales/politica_cookies.html'), name='politica_cookies'),
    
    
    # Resto de aplicaciones
    path('', include('core.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('negocio/', include('negocio.urls')),
    path('reservas/', include('reservas.urls')),
    path('plano/', include('plano.urls')),
]