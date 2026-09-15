from functools import wraps
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def administrador_required(view_func):

    @wraps(view_func)
    def validar_acceso(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists():
            return view_func(request, *args, **kwargs)

        return redirect('inicio')

    return validar_acceso


def personal_required(view_func):

    @wraps(view_func)
    def validar_acceso(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if request.user.is_superuser or request.user.groups.filter(name__in=['Administrador', 'Empleado']).exists():
            return view_func(request, *args, **kwargs)

        return redirect('inicio')

    return validar_acceso