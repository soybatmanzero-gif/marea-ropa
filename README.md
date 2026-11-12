# MAREA Ropa — tienda de ropa en Django

Proyecto de programación: tienda de ropa con login de dos roles (admin y cliente).

## Cómo correrlo

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (en Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py makemigrations tienda
python manage.py migrate
python manage.py seed          # crea usuarios, las 8 prendas con sus fotos y los 2 videos
python manage.py runserver
```

Abre http://127.0.0.1:8000/ — lo primero que aparece es el login.

| Rol     | Usuario   | Contraseña     | Entra a                    |
|---------|-----------|----------------|----------------------------|
| Admin   | `admin`   | `Admin12345!`  | Panel de métricas + CRUD   |
| Cliente | `cliente` | `Cliente12345!`| Home con carrusel          |

Los usuarios nuevos que se registran en `/registro/` siempre son clientes.
El rol de admin es `is_staff=True` (se asigna desde `/django-admin/`).

## Rúbrica → dónde está

| Punto de la rúbrica | Dónde |
|---|---|
| Login antes de todo, 2 tipos de usuario | `tienda/views.py` (`raiz`, `inicio`, `admin_required`), `templates/registration/` |
| Home admin (métricas) / home cliente | `dashboard_admin.html` (Chart.js) / `home_cliente.html` (carrusel) |
| Producto / servicio (ropa) | modelo `Producto`, `catalogo.html` |
| Identidad: logo, paleta, slogan, letras | `static/img/logo.svg`, `static/css/style.css`, `identidad.html` |
| Menú | `templates/base.html` |
| Capturar ubicación + mapa/cercanía | `ubicacion.html` (Leaflet + OpenStreetMap, distancia Haversine) |
| CRUD | productos: crear / ver / editar / borrar (solo admin) |
| Blog (chat) | `blog.html` (se actualiza cada 3 s) |
| Videos | `videos.html` (YouTube o .mp4; el admin los agrega) |
| Encuesta | `encuesta.html`; resultados en el panel admin |
| Compras | carrito, confirmar pedido y "Mis pedidos" (cliente); lista de pedidos y estado (admin) |
| Tomar fotos | `fotos.html` (cámara del navegador o galería) |

## Personalizar

En `marea/settings.py` cambia `TIENDA_LAT`, `TIENDA_LNG`, `TIENDA_NOMBRE`, `TIENDA_SLOGAN` y `TIENDA_DIRECCION` (la ubicación elegida) y los datos de la página **Autora** (`AUTORA_NOMBRE` y `AUTORA_DATOS`). La foto está en `static/img/autora.jpg`.

## Mapas de Google (página Autora)

- **Etapa 1 (iframe):** funciona sin llave.
- **Etapa 3 (mapa interactivo):** necesita la API Key en la variable de entorno `GOOGLE_MAPS_API_KEY`. En PowerShell, antes de `runserver`: `$env:GOOGLE_MAPS_API_KEY="tu-llave"`. Nunca la escribas en el código ni la subas a GitHub.
- En Google Cloud restringe la llave por **HTTP referrers** (`https://TU-APP.onrender.com/*`, `http://127.0.0.1:8000/*`, `http://localhost:8000/*`) y por **API** (solo Maps JavaScript API).

## Publicar en Render

Build Command: `bash build.sh`  ·  Start Command: `gunicorn marea.wsgi:application`

Variables de entorno: `DATABASE_URL` (la Service URI de Aiven), `SECRET_KEY`, `ADMIN_PASSWORD`, `CLIENTE_PASSWORD` y `GOOGLE_MAPS_API_KEY`.

## Notas

- En Render gratis el disco no es permanente: las fotos que tomen los usuarios se pierden al reiniciar o volver a publicar. Las prendas y videos de `media/` sí se conservan.
- La cámara y la geolocalización del navegador solo funcionan en `localhost` o con HTTPS.
- Mapa, gráficas y tipografías se cargan desde CDN, por lo que necesitas internet.
- Las fotos de las prendas están en `media/productos/` y los videos en `media/videos/`. `seed` los carga en la base y se puede correr varias veces sin duplicar nada.
- Los dos videos son de @penumbra_designs (TikTok); sus créditos aparecen en la descripción de cada video.
- El logotipo es original. El fondo de todo el sitio (`static/img/fondo.jpg`) es un recorte de la imagen de peces que tú elegiste; si algún día publicas el sitio, revisa que tengas permiso de usarla.
- Para cambiar el difuminado del fondo o qué tan claro es el velo, edita `--desenfoque` y `--velo` al inicio de `static/css/style.css` (el login tiene su propio velo en la sección "Login" del mismo archivo).
