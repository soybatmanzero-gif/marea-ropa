from django.conf import settings


def marca(request):
    """Datos de la marca disponibles en todas las plantillas."""
    return {
        "TIENDA_NOMBRE": settings.TIENDA_NOMBRE,
        "TIENDA_SLOGAN": settings.TIENDA_SLOGAN,
    }
