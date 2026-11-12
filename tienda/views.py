import base64
import json
import uuid
from functools import wraps
from decimal import Decimal
from math import asin, cos, radians, sin, sqrt

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Avg, Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import EncuestaForm, PedidoForm, ProductoForm, RegistroForm, VideoForm
from .models import Foto, Mensaje, Pedido, PedidoItem, Producto, RespuestaEncuesta, UbicacionUsuario, Video


# ---------------------------------------------------------------- utilidades
def admin_required(view):
    """Solo usuarios administradores (is_staff). Los clientes reciben 403."""

    @wraps(view)
    @login_required
    def envuelta(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return envuelta


def distancia_km(lat1, lng1, lat2, lng2):
    """Distancia en km entre dos puntos (fórmula de Haversine)."""
    r = 6371.0
    dlat, dlng = radians(lat2 - lat1), radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 2 * r * asin(sqrt(a))


def leer_json(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


# ---------------------------------------------------------- acceso y homes
def raiz(request):
    """Lo primero que se ve es el login."""
    if request.user.is_authenticated:
        return redirect("inicio")
    return redirect("login")


def registro(request):
    if request.user.is_authenticated:
        return redirect("inicio")
    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()  # los registros nuevos siempre son clientes
        login(request, usuario)
        messages.success(request, "¡Bienvenido a la corriente!")
        return redirect("inicio")
    return render(request, "registration/registro.html", {"form": form})


@login_required
def inicio(request):
    """Bifurca según el rol: admin -> métricas, cliente -> home con carrusel."""
    if request.user.is_staff:
        return redirect("dashboard")
    destacados = Producto.objects.filter(destacado=True)[:4] or Producto.objects.all()[:4]
    return render(
        request,
        "tienda/home_cliente.html",
        {"destacados": destacados, "categorias": Producto.CATEGORIAS},
    )


@admin_required
def dashboard(request):
    por_categoria = list(
        Producto.objects.values("categoria").annotate(n=Count("id")).order_by("categoria")
    )
    nombres = dict(Producto.CATEGORIAS)
    cat_labels = [nombres.get(c["categoria"], c["categoria"]) for c in por_categoria]
    cat_values = [c["n"] for c in por_categoria]

    sat_counts = {i: 0 for i in range(1, 6)}
    for fila in RespuestaEncuesta.objects.values("satisfaccion").annotate(n=Count("id")):
        sat_counts[fila["satisfaccion"]] = fila["n"]

    fav = list(
        RespuestaEncuesta.objects.values("categoria_favorita").annotate(n=Count("id")).order_by("-n")
    )
    fav_top = nombres.get(fav[0]["categoria_favorita"]) if fav else None

    total_respuestas = RespuestaEncuesta.objects.count()
    si_recomienda = RespuestaEncuesta.objects.filter(recomendaria=True).count()

    contexto = {
        "total_clientes": User.objects.filter(is_staff=False).count(),
        "total_productos": Producto.objects.count(),
        "stock_total": Producto.objects.aggregate(s=Sum("stock"))["s"] or 0,
        "total_mensajes": Mensaje.objects.count(),
        "total_fotos": Foto.objects.count(),
        "total_pedidos": Pedido.objects.count(),
        "ventas_total": Pedido.objects.exclude(estado="cancelado").aggregate(s=Sum("total"))["s"] or 0,
        "total_respuestas": total_respuestas,
        "promedio_satisfaccion": RespuestaEncuesta.objects.aggregate(a=Avg("satisfaccion"))["a"],
        "porcentaje_recomienda": round(100 * si_recomienda / total_respuestas) if total_respuestas else None,
        "categoria_top": fav_top,
        "ubicaciones": UbicacionUsuario.objects.select_related("usuario")[:8],
        "promedio_distancia": UbicacionUsuario.objects.aggregate(a=Avg("distancia_km"))["a"],
        "respuestas": RespuestaEncuesta.objects.select_related("usuario")[:5],
        "datos_graficas": {
            "categorias": {"labels": cat_labels, "values": cat_values},
            "satisfaccion": {"labels": ["1", "2", "3", "4", "5"], "values": list(sat_counts.values())},
        },
    }
    return render(request, "tienda/dashboard_admin.html", contexto)


# --------------------------------------------------------- catálogo y CRUD
@login_required
def catalogo(request):
    productos = Producto.objects.all()
    categoria = request.GET.get("categoria")
    q = request.GET.get("q", "").strip()
    if categoria:
        productos = productos.filter(categoria=categoria)
    if q:
        productos = productos.filter(nombre__icontains=q)
    return render(
        request,
        "tienda/catalogo.html",
        {"productos": productos, "categorias": Producto.CATEGORIAS, "categoria_activa": categoria, "q": q},
    )


@admin_required
def producto_crear(request):
    form = ProductoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto creado.")
        return redirect("catalogo")
    return render(request, "tienda/producto_form.html", {"form": form, "titulo": "Nuevo producto"})


@admin_required
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto actualizado.")
        return redirect("catalogo")
    return render(request, "tienda/producto_form.html", {"form": form, "titulo": f"Editar: {producto.nombre}"})


@admin_required
def producto_borrar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        messages.success(request, "Producto eliminado.")
        return redirect("catalogo")
    return render(request, "tienda/producto_borrar.html", {"producto": producto})


# ------------------------------------------------------- ubicación y mapa
@login_required
def ubicacion(request):
    ultima = request.user.ubicaciones.first()
    return render(
        request,
        "tienda/ubicacion.html",
        {
            "tienda": {
                "lat": settings.TIENDA_LAT,
                "lng": settings.TIENDA_LNG,
                "nombre": settings.TIENDA_NOMBRE,
                "direccion": settings.TIENDA_DIRECCION,
            },
            "ultima": ultima,
        },
    )


@login_required
@require_POST
def guardar_ubicacion(request):
    datos = leer_json(request)
    try:
        lat, lng = float(datos["lat"]), float(datos["lng"])
        assert -90 <= lat <= 90 and -180 <= lng <= 180
    except (TypeError, KeyError, ValueError, AssertionError):
        return JsonResponse({"error": "Ubicación inválida"}, status=400)
    km = distancia_km(lat, lng, settings.TIENDA_LAT, settings.TIENDA_LNG)
    UbicacionUsuario.objects.create(usuario=request.user, latitud=lat, longitud=lng, distancia_km=km)
    return JsonResponse({"km": round(km, 2)})


# --------------------------------------------------------------- blog/chat
@login_required
def blog(request):
    recientes = list(Mensaje.objects.select_related("usuario").order_by("-id")[:50])[::-1]
    return render(request, "tienda/blog.html", {"mensajes": recientes})


def _mensaje_json(m):
    return {
        "id": m.id,
        "usuario": m.usuario.username,
        "es_admin": m.usuario.is_staff,
        "texto": m.texto,
        "hora": m.creado.astimezone().strftime("%d/%m %H:%M"),
    }


@login_required
def mensajes_api(request):
    try:
        despues = int(request.GET.get("despues", 0))
    except ValueError:
        despues = 0
    nuevos = Mensaje.objects.select_related("usuario").filter(id__gt=despues).order_by("id")[:100]
    return JsonResponse({"mensajes": [_mensaje_json(m) for m in nuevos]})


@login_required
@require_POST
def enviar_mensaje(request):
    datos = leer_json(request) or {}
    texto = str(datos.get("texto", "")).strip()[:500]
    if not texto:
        return JsonResponse({"error": "Mensaje vacío"}, status=400)
    m = Mensaje.objects.create(usuario=request.user, texto=texto)
    return JsonResponse(_mensaje_json(m))


# ------------------------------------------------------------------ videos
@login_required
def videos(request):
    form = None
    if request.user.is_staff:
        form = VideoForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, "Video agregado.")
            return redirect("videos")
    return render(request, "tienda/videos.html", {"videos": Video.objects.all(), "form": form})


@admin_required
@require_POST
def video_borrar(request, pk):
    get_object_or_404(Video, pk=pk).delete()
    messages.success(request, "Video eliminado.")
    return redirect("videos")


# ---------------------------------------------------------------- encuesta
@login_required
def encuesta(request):
    form = EncuestaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        respuesta = form.save(commit=False)
        respuesta.usuario = request.user
        respuesta.save()
        messages.success(request, "¡Gracias por responder!")
        return redirect("encuesta")
    return render(
        request,
        "tienda/encuesta.html",
        {"form": form, "mis_respuestas": request.user.respuestas.count()},
    )


# ------------------------------------------------------------------- fotos
@login_required
def fotos(request):
    if request.user.is_staff:
        galeria = Foto.objects.select_related("usuario")[:60]
    else:
        galeria = request.user.fotos.all()[:60]
    return render(request, "tienda/fotos.html", {"fotos": galeria})


@login_required
@require_POST
def subir_foto(request):
    """Recibe la foto como data URL (base64) tomada desde la cámara del navegador."""
    datos = leer_json(request) or {}
    imagen = str(datos.get("imagen", ""))
    if not imagen.startswith("data:image/") or "," not in imagen:
        return JsonResponse({"error": "Imagen inválida"}, status=400)
    cabecera, b64 = imagen.split(",", 1)
    extension = "png" if "png" in cabecera else "jpg"
    try:
        contenido = base64.b64decode(b64, validate=True)
    except ValueError:
        return JsonResponse({"error": "Imagen inválida"}, status=400)
    if len(contenido) > 8 * 1024 * 1024:
        return JsonResponse({"error": "La imagen pesa demasiado"}, status=400)
    foto = Foto(usuario=request.user, descripcion=str(datos.get("descripcion", ""))[:120])
    foto.imagen.save(f"{uuid.uuid4().hex}.{extension}", ContentFile(contenido), save=True)
    return JsonResponse({"url": foto.imagen.url})


@login_required
@require_POST
def borrar_foto(request, pk):
    foto = get_object_or_404(Foto, pk=pk)
    if foto.usuario_id != request.user.id and not request.user.is_staff:
        raise PermissionDenied
    foto.delete()
    return redirect("fotos")


# --------------------------------------------------------------- identidad
@login_required
def identidad(request):
    return render(request, "tienda/identidad.html")


# ------------------------------------------------------------------ autora
def url_mapa_iframe():
    """URL del iframe de la Etapa 1 (no necesita API Key)."""
    if settings.GOOGLE_MAPS_EMBED_URL:
        return settings.GOOGLE_MAPS_EMBED_URL
    return f"https://www.google.com/maps?q={settings.TIENDA_LAT},{settings.TIENDA_LNG}&z=16&output=embed"


@login_required
def autora(request):
    return render(
        request,
        "tienda/autora.html",
        {
            "autora_nombre": settings.AUTORA_NOMBRE,
            "autora_datos": settings.AUTORA_DATOS,
            "ubicacion": {
                "lat": settings.TIENDA_LAT,
                "lng": settings.TIENDA_LNG,
                "nombre": settings.TIENDA_NOMBRE,
                "direccion": settings.TIENDA_DIRECCION,
            },
            "iframe_url": url_mapa_iframe(),
            "maps_key": settings.GOOGLE_MAPS_API_KEY,
        },
    )


# ------------------------------------------------------- carrito y compras
def cliente_required(view):
    """Solo clientes: el administrador gestiona pedidos, no compra."""

    @wraps(view)
    @login_required
    def envuelta(request, *args, **kwargs):
        if request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return envuelta


def _lineas_carrito(request):
    """Devuelve las líneas del carrito (producto, cantidad, subtotal) y el total."""
    carrito = request.session.get("carrito", {})
    productos = Producto.objects.in_bulk([int(k) for k in carrito])
    lineas, total = [], Decimal("0")
    for k, cantidad in carrito.items():
        p = productos.get(int(k))
        if not p:
            continue
        subtotal = p.precio * cantidad
        lineas.append({"producto": p, "cantidad": cantidad, "subtotal": subtotal})
        total += subtotal
    return lineas, total


@cliente_required
def carrito(request):
    lineas, total = _lineas_carrito(request)
    return render(request, "tienda/carrito.html", {"lineas": lineas, "total": total})


@cliente_required
@require_POST
def carrito_agregar(request, pk):
    p = get_object_or_404(Producto, pk=pk)
    carrito = request.session.get("carrito", {})
    actual = carrito.get(str(pk), 0)
    if actual + 1 > p.stock:
        messages.error(request, f"No hay más piezas de {p.nombre} disponibles.")
    else:
        carrito[str(pk)] = actual + 1
        request.session["carrito"] = carrito
        messages.success(request, f"{p.nombre} se agregó al carrito.")
    destino = request.POST.get("siguiente", "")
    if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        return redirect(destino)
    return redirect("catalogo")


@cliente_required
@require_POST
def carrito_actualizar(request, pk):
    p = get_object_or_404(Producto, pk=pk)
    carrito = request.session.get("carrito", {})
    try:
        cantidad = int(request.POST.get("cantidad", 1))
    except ValueError:
        cantidad = 1
    if cantidad <= 0:
        carrito.pop(str(pk), None)
    else:
        if cantidad > p.stock:
            cantidad = p.stock
            messages.info(request, f"Solo hay {p.stock} piezas de {p.nombre}.")
        carrito[str(pk)] = cantidad
    request.session["carrito"] = carrito
    return redirect("carrito")


@cliente_required
@require_POST
def carrito_quitar(request, pk):
    carrito = request.session.get("carrito", {})
    carrito.pop(str(pk), None)
    request.session["carrito"] = carrito
    return redirect("carrito")


@cliente_required
def comprar(request):
    """Confirma el pedido: valida existencias, guarda el pedido y descuenta el stock."""
    lineas, total = _lineas_carrito(request)
    if not lineas:
        messages.info(request, "Tu carrito está vacío.")
        return redirect("catalogo")
    form = PedidoForm(request.POST or None, initial={"nombre": request.user.get_full_name() or request.user.username})
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            productos = Producto.objects.select_for_update().in_bulk([l["producto"].pk for l in lineas])
            for l in lineas:
                if l["cantidad"] > productos[l["producto"].pk].stock:
                    messages.error(request, f"Ya no hay suficientes piezas de {l['producto'].nombre}. Revisa tu carrito.")
                    return redirect("carrito")
            pedido = form.save(commit=False)
            pedido.usuario = request.user
            pedido.total = sum(productos[l["producto"].pk].precio * l["cantidad"] for l in lineas)
            pedido.save()
            for l in lineas:
                p = productos[l["producto"].pk]
                PedidoItem.objects.create(pedido=pedido, producto=p, nombre=p.nombre, precio=p.precio, cantidad=l["cantidad"])
                p.stock -= l["cantidad"]
                p.save(update_fields=["stock"])
        request.session["carrito"] = {}
        messages.success(request, "¡Gracias por tu compra! Tu pedido quedó registrado.")
        return redirect("pedido_detalle", pk=pedido.pk)
    return render(request, "tienda/comprar.html", {"form": form, "lineas": lineas, "total": total})


@login_required
def pedidos(request):
    """Cliente: sus pedidos. Administrador: todos los pedidos."""
    lista = Pedido.objects.select_related("usuario").prefetch_related("items")
    if not request.user.is_staff:
        lista = lista.filter(usuario=request.user)
    return render(request, "tienda/pedidos.html", {"pedidos": lista, "estados": Pedido.ESTADOS})


@login_required
def pedido_detalle(request, pk):
    pedido = get_object_or_404(Pedido.objects.prefetch_related("items"), pk=pk)
    if pedido.usuario_id != request.user.id and not request.user.is_staff:
        raise PermissionDenied
    return render(request, "tienda/pedido_detalle.html", {"pedido": pedido, "estados": Pedido.ESTADOS})


@admin_required
@require_POST
def pedido_estado(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    nuevo = request.POST.get("estado")
    if nuevo in dict(Pedido.ESTADOS):
        pedido.estado = nuevo
        pedido.save(update_fields=["estado"])
        messages.success(request, f"Pedido #{pedido.pk} marcado como {pedido.get_estado_display().lower()}.")
    return redirect("pedidos")
