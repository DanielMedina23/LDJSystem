from functools import wraps
import logging
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def rate_limit(max_requests=45, window_seconds=60):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', 'unknown')

            cache_key = f"rate_limit_{ip}_{request.path}"
            request_count = cache.get(cache_key, 0)

            if request_count >= max_requests:
                logger.warning(f"SECURITY: Rate limit excedido para IP {ip} en la ruta {request.path}")
                return JsonResponse(
                    {"ok": False, "error": "Demasiadas solicitudes. Límite de velocidad excedido."},
                    status=429
                )

            if request_count == 0:
                cache.set(cache_key, 1, window_seconds)
            else:
                cache.incr(cache_key)

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator