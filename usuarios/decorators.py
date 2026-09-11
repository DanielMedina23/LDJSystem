from django.shortcuts import redirect

def administrador_required(view_func):

    def validar_acceso(request, *args, **kwargs):

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if request.user.groups.filter(name='Administrador').exists():
            return view_func(request, *args, **kwargs)

        return redirect('inicio')

    return validar_acceso

#DECORADOR PARA LOS EMPLEADOS
def personal_required(view_func):

    def validar_acceso(request, *args, **kwargs):

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if request.user.groups.filter(
            name__in=['Administrador', 'Empleado']
        ).exists():
            return view_func(request, *args, **kwargs)

        return redirect('inicio')

    return validar_acceso