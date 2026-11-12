import re

from django.conf import settings
from django.db import models


class Producto(models.Model):
    CATEGORIAS = [
        ("camisas", "Camisas y playeras"),
        ("pantalones", "Pantalones"),
        ("vestidos", "Vestidos"),
        ("chamarras", "Chamarras"),
        ("accesorios", "Accesorios"),
    ]

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="camisas")
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    talla = models.CharField(max_length=20, default="M", help_text="Ej. S, M, L o 28-34")
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    destacado = models.BooleanField(default=False, help_text="Aparece en la página principal")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return self.nombre


class UbicacionUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ubicaciones")
    latitud = models.FloatField()
    longitud = models.FloatField()
    distancia_km = models.FloatField(help_text="Distancia a la tienda en kilómetros")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.usuario} a {self.distancia_km:.1f} km"


class Mensaje(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mensajes")
    texto = models.CharField(max_length=500)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.usuario}: {self.texto[:30]}"


class Video(models.Model):
    titulo = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=250, blank=True)
    url = models.URLField(help_text="Enlace de YouTube o de un archivo de video (.mp4)")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return self.titulo

    @property
    def embed_url(self):
        """Devuelve la URL de incrustación si es de YouTube; si no, None."""
        m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})", self.url)
        return f"https://www.youtube.com/embed/{m.group(1)}" if m else None


class RespuestaEncuesta(models.Model):
    SATISFACCION = [(i, str(i)) for i in range(1, 6)]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="respuestas")
    satisfaccion = models.PositiveSmallIntegerField(choices=SATISFACCION)
    categoria_favorita = models.CharField(max_length=20, choices=Producto.CATEGORIAS)
    recomendaria = models.BooleanField(default=True)
    comentario = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"Encuesta de {self.usuario} ({self.satisfaccion}/5)"


class Foto(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fotos")
    imagen = models.ImageField(upload_to="fotos/")
    descripcion = models.CharField(max_length=120, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"Foto de {self.usuario}"


class Pedido(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("entregado", "Entregado"),
        ("cancelado", "Cancelado"),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pedidos")
    nombre = models.CharField("Nombre de quien recibe", max_length=120)
    telefono = models.CharField("Teléfono de contacto", max_length=20)
    notas = models.TextField("Notas para la entrega (opcional)", blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=12, choices=ESTADOS, default="pendiente")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"Pedido #{self.pk} de {self.usuario}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(max_length=120)  # copia del nombre, por si el producto se borra después
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.nombre}"
