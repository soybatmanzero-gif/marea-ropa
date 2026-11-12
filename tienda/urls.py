from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.raiz, name="raiz"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),
    path("inicio/", views.inicio, name="inicio"),
    path("panel/", views.dashboard, name="dashboard"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("catalogo/nuevo/", views.producto_crear, name="producto_crear"),
    path("catalogo/<int:pk>/editar/", views.producto_editar, name="producto_editar"),
    path("catalogo/<int:pk>/borrar/", views.producto_borrar, name="producto_borrar"),
    path("carrito/", views.carrito, name="carrito"),
    path("carrito/agregar/<int:pk>/", views.carrito_agregar, name="carrito_agregar"),
    path("carrito/actualizar/<int:pk>/", views.carrito_actualizar, name="carrito_actualizar"),
    path("carrito/quitar/<int:pk>/", views.carrito_quitar, name="carrito_quitar"),
    path("comprar/", views.comprar, name="comprar"),
    path("pedidos/", views.pedidos, name="pedidos"),
    path("pedidos/<int:pk>/", views.pedido_detalle, name="pedido_detalle"),
    path("pedidos/<int:pk>/estado/", views.pedido_estado, name="pedido_estado"),
    path("mapa/", views.ubicacion, name="ubicacion"),
    path("mapa/guardar/", views.guardar_ubicacion, name="guardar_ubicacion"),
    path("blog/", views.blog, name="blog"),
    path("blog/mensajes/", views.mensajes_api, name="mensajes_api"),
    path("blog/enviar/", views.enviar_mensaje, name="enviar_mensaje"),
    path("videos/", views.videos, name="videos"),
    path("videos/<int:pk>/borrar/", views.video_borrar, name="video_borrar"),
    path("encuesta/", views.encuesta, name="encuesta"),
    path("fotos/", views.fotos, name="fotos"),
    path("fotos/subir/", views.subir_foto, name="subir_foto"),
    path("fotos/<int:pk>/borrar/", views.borrar_foto, name="borrar_foto"),
    path("identidad/", views.identidad, name="identidad"),
    path("autora/", views.autora, name="autora"),
]
