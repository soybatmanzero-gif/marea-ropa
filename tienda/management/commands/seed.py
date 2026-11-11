import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from tienda.models import Mensaje, Producto, Video

# nombre, categoría, precio, talla, stock, destacado (sale en la home), foto (dentro de media/)
CATALOGO = [
    ("Playera Cardumen", "camisas", 349, "M", 25, True, "productos/playera-cardumen.jpg"),
    ("Camisa Mar Azul", "camisas", 499, "L", 14, True, "productos/camisa-mar-azul.jpg"),
    ("Jeans Resaca", "pantalones", 899, "30", 12, False, "productos/jeans-resaca.jpg"),
    ("Jeans Campana", "pantalones", 849, "28", 10, False, "productos/jeans-campana.jpg"),
    ("Chamarra Biker", "chamarras", 1299, "M", 7, True, "productos/chamarra-biker.jpg"),
    ("Vestido Marea Alta", "vestidos", 699, "S", 9, True, "productos/vestido-marea-alta.jpg"),
    ("Bufanda Cuadros", "accesorios", 329, "Única", 15, False, "productos/bufanda-cuadros.jpg"),
    ("Gorra Tiburón", "accesorios", 249, "Única", 30, False, "productos/gorra-tiburon.jpg"),
]

# Productos de ejemplo de la primera versión: se borran para que no queden sin foto.
ANTERIORES = ["Playera Oleaje", "Camisa Cardumen", "Pantalón Corriente", "Chamarra Abisal", "Gorra Ámbar", "Bufanda Espuma"]

# título, descripción, archivo (dentro de media/videos/)
VIDEOS = [
    ("Corbata de pez interactiva", "Créditos: @penumbra_designs en TikTok.", "/media/videos/video_1.mp4"),
    ("Outfits inspirados en tiburón ballena", "Créditos: @penumbra_designs en TikTok.", "/media/videos/video_2.mp4"),
]


class Command(BaseCommand):
    help = (
        "Crea los usuarios de prueba, y las prendas y videos si todavía no hay. "
        "Se puede correr varias veces sin duplicar ni pisar tus cambios. "
        "Con --catalogo vuelve a cargar el catálogo y los videos originales."
    )

    def add_arguments(self, parser):
        parser.add_argument("--catalogo", action="store_true", help="Vuelve a cargar las prendas y los videos originales.")

    def handle(self, *args, **options):
        # En tu computadora hay contraseñas de práctica; en Render se piden por variable de entorno.
        admin_pw = os.environ.get("ADMIN_PASSWORD") or ("Admin12345!" if settings.DEBUG else None)
        cliente_pw = os.environ.get("CLIENTE_PASSWORD") or ("Cliente12345!" if settings.DEBUG else None)

        if not User.objects.filter(username="admin").exists():
            if admin_pw:
                User.objects.create_superuser("admin", "admin@marea.test", admin_pw)
            else:
                self.stderr.write("Falta la variable ADMIN_PASSWORD: no se creó el usuario admin.")

        cliente = User.objects.filter(username="cliente").first()
        if not cliente:
            if cliente_pw:
                cliente = User.objects.create_user("cliente", "cliente@marea.test", cliente_pw)
            else:
                self.stderr.write("Falta la variable CLIENTE_PASSWORD: no se creó el usuario cliente.")

        if options["catalogo"] or not Producto.objects.exists():
            Producto.objects.filter(nombre__in=ANTERIORES).delete()
            for nombre, categoria, precio, talla, stock, destacado, foto in CATALOGO:
                Producto.objects.update_or_create(
                    nombre=nombre,
                    defaults={
                        "categoria": categoria, "precio": precio, "talla": talla, "stock": stock,
                        "destacado": destacado, "imagen": foto, "descripcion": "",
                    },
                )

        if options["catalogo"] or not Video.objects.exists():
            for titulo, descripcion, url in VIDEOS:
                Video.objects.update_or_create(titulo=titulo, defaults={"descripcion": descripcion, "url": url})

        if cliente and not Mensaje.objects.exists():
            Mensaje.objects.create(usuario=cliente, texto="¡Hola! ¿Cuándo llegan las chamarras nuevas?")

        self.stdout.write(self.style.SUCCESS(f"Listo: {Producto.objects.count()} prendas y {Video.objects.count()} videos."))
        if settings.DEBUG:
            self.stdout.write("Usuarios de práctica:  admin / Admin12345!   cliente / Cliente12345!")
