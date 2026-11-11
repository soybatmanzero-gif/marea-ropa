from django.contrib import admin

from .models import Foto, Mensaje, Producto, RespuestaEncuesta, UbicacionUsuario, Video

admin.site.register(Producto)
admin.site.register(UbicacionUsuario)
admin.site.register(Mensaje)
admin.site.register(Video)
admin.site.register(RespuestaEncuesta)
admin.site.register(Foto)
