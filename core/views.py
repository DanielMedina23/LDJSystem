from django.shortcuts import render
from usuarios.forms import RegistroClienteForm

# Create your views here.

#Vista del inicio principal
def inicio(request):
    formulario = RegistroClienteForm()

    return render(request, 'core/inicio.html', {'formulario': formulario})