import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Render define RENDER=true automáticamente; en tu computadora no existe.
EN_RENDER = os.environ.get("RENDER") == "true"

# En tu computadora DEBUG está prendido; en Render se apaga solo.
DEBUG = os.environ.get("DEBUG", "0" if EN_RENDER else "1") == "1"

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "clave-solo-para-desarrollo-local"
    else:
        raise RuntimeError("Falta la variable de entorno SECRET_KEY (ponla en Render > Environment).")

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost", ".onrender.com"]
    ALLOWED_HOSTS += [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = ["https://*.onrender.com", "https://*.devtunnels.ms"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tienda",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if not DEBUG:
    # Sirve los archivos estáticos (CSS, imágenes) en producción.
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "marea.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tienda.context.marca",
                "tienda.context.carrito",
            ],
        },
    },
]

WSGI_APPLICATION = "marea.wsgi.application"

# Base de datos: si existe DATABASE_URL (la de Aiven) se usa esa; si no, SQLite local.
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    import dj_database_url

    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if DEBUG
        else "whitenoise.storage.CompressedStaticFilesStorage"
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "inicio"
LOGOUT_REDIRECT_URL = "login"

# Permite que OpenStreetMap vea de qué sitio viene la petición (si no, bloquea el mapa con 403).
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Las fotos de la cámara viajan en base64, necesitan más espacio que el default.
DATA_UPLOAD_MAX_MEMORY_SIZE = 15 * 1024 * 1024

# Detrás del proxy de Render el sitio va por HTTPS.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ---- Datos de la tienda ----
TIENDA_NOMBRE = "MAREA Ropa"
TIENDA_SLOGAN = "Sigue tu propia corriente."

# La tienda es virtual, así que se usa un punto de entrega como "ubicación elegida".
# Verifica las coordenadas en Google Maps (clic derecho sobre el lugar > copiar coordenadas) y cámbialas si hace falta.
TIENDA_LAT = 19.6426685
TIENDA_LNG = -99.1258486
TIENDA_DIRECCION = "Universidad Politécnica del Valle de México, Av. Mexiquense s/n, Tultitlán, Estado de México"

# ---- Google Maps ----
# La API Key NO se escribe aquí: se pone como variable de entorno (en Render y en tu computadora).
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
# Opcional: si tu guía pide copiar el iframe desde Google Maps (Compartir > Insertar un mapa), pega aquí solo el src.
GOOGLE_MAPS_EMBED_URL = os.environ.get("GOOGLE_MAPS_EMBED_URL", "")

# ---- Página "Autora" (foto y datos personales) ----
AUTORA_NOMBRE = "Yuleang Ixchel Arteaga Ley"
AUTORA_DATOS = [
    ("Universidad", "Universidad Politécnica del Valle de México (UPVM)"),
    ("Proyecto", "MAREA Ropa — tienda de ropa virtual hecha con Django"),
    # Agrega lo que pida tu profe, por ejemplo:
    # ("Carrera", "..."),
    # ("Matrícula", "..."),
    # ("Correo", "..."),
]
