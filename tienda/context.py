from django.conf import settings


def marca(request):
    """Datos de la marca disponibles en todas las plantillas."""
    return {
        "TIENDA_NOMBRE": settings.TIENDA_NOMBRE,
        "TIENDA_SLOGAN": settings.TIENDA_SLOGAN,
    }


def carrito(request):
    """Cantidad de piezas en el carrito (para el menú)."""
    if not request.user.is_authenticated or request.user.is_staff:
        return {"carrito_cantidad": 0}
    return {"carrito_cantidad": sum(request.session.get("carrito", {}).values())}
