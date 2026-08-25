from pathlib import Path
import os
from datetime import timedelta

import dj_database_url


# ============================================================
# BASE DU PROJET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SÉCURITÉ
# ============================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-change-this-key-in-production"
)

DEBUG = os.getenv("DEBUG", "True").lower() == "true"


# ============================================================
# HÔTES AUTORISÉS
# ============================================================

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)


# ============================================================
# GEODJANGO
# ============================================================

# Configuration QGIS uniquement en local Windows.
# Render utilise son environnement Linux et n'utilise pas ces chemins.

if os.name == "nt":

    QGIS_BIN = r"C:\Program Files\QGIS 4.0.3\bin"
    QGIS_PROJ = r"C:\Program Files\QGIS 4.0.3\share\proj"
    QGIS_GDAL_DATA = r"C:\Program Files\QGIS 4.0.3\share\gdal"

    if os.path.exists(QGIS_BIN):
        os.add_dll_directory(QGIS_BIN)

        os.environ["PATH"] = (
            QGIS_BIN
            + os.pathsep
            + os.environ.get("PATH", "")
        )

    if os.path.exists(QGIS_PROJ):
        os.environ["PROJ_LIB"] = QGIS_PROJ
        os.environ["PROJ_DATA"] = QGIS_PROJ

    if os.path.exists(QGIS_GDAL_DATA):
        os.environ["GDAL_DATA"] = QGIS_GDAL_DATA

    GDAL_LIBRARY_PATH = os.path.join(
        QGIS_BIN,
        "gdal313.dll"
    )

    GEOS_LIBRARY_PATH = os.path.join(
        QGIS_BIN,
        "geos_c.dll"
    )


# ============================================================
# APPLICATIONS INSTALLÉES
# ============================================================

INSTALLED_APPS = [

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # GeoDjango
    "django.contrib.gis",

    # API REST
    "rest_framework",
    "rest_framework_gis",
    "django_filters",

    # CORS
    "corsheaders",

    # Swagger
    "drf_yasg",

    # Application
    "sante",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",

    # Fichiers statiques en production
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URLS
# ============================================================

ROOT_URLCONF = "config.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# BASE DE DONNÉES POSTGRESQL / POSTGIS
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")


if DATABASE_URL:

    # Production : Render PostgreSQL / PostGIS
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

else:

    # Développement local
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": "infrastructure_sanitaire",
            "USER": "postgres",
            "PASSWORD": "deme",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }


# ============================================================
# VALIDATION DES MOTS DE PASSE
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ============================================================
# LANGUE / TEMPS
# ============================================================

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Africa/Dakar"

USE_I18N = True

USE_TZ = True


# ============================================================
# FICHIERS STATIQUES
# ============================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# WhiteNoise
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },

    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}


# ============================================================
# FICHIERS MÉDIAS
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),

    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),

    "DEFAULT_PAGINATION_CLASS":
        "rest_framework.pagination.PageNumberPagination",

    "PAGE_SIZE": 20,

    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}


# ============================================================
# JWT
# ============================================================

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME":
        timedelta(hours=24),

    "REFRESH_TOKEN_LIFETIME":
        timedelta(days=7),

    "ROTATE_REFRESH_TOKENS":
        True,

    "BLACKLIST_AFTER_ROTATION":
        True,

    "UPDATE_LAST_LOGIN":
        True,

    "ALGORITHM":
        "HS256",

    "SIGNING_KEY":
        SECRET_KEY,

    "VERIFYING_KEY":
        None,

    "AUDIENCE":
        None,

    "ISSUER":
        None,

    "AUTH_HEADER_TYPES":
        ("Bearer",),

    "USER_ID_FIELD":
        "id",

    "USER_ID_CLAIM":
        "user_id",
}


# ============================================================
# CORS
# ============================================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True


# ============================================================
# CSRF
# ============================================================

CSRF_TRUSTED_ORIGINS = []

render_url = os.getenv("RENDER_EXTERNAL_URL")

if render_url:
    CSRF_TRUSTED_ORIGINS.append(render_url)


# ============================================================
# SWAGGER / OPENAPI
# ============================================================

SWAGGER_SETTINGS = {

    "SECURITY_DEFINITIONS": {

        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description":
                "JWT Token : Bearer <votre_token>",
        }
    },

    "USE_SESSION_AUTH": False,

    "JSON_EDITOR": True,
}


# ============================================================
# LOGGING
# ============================================================

LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


LOGGING = {

    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {

        "verbose": {
            "format":
                "{levelname} {asctime} {module} "
                "{process:d} {thread:d} {message}",
            "style": "{",
        },

        "simple": {
            "format":
                "{levelname} {asctime} {message}",
            "style": "{",
        },
    },

    "handlers": {

        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },

        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "django.log",
            "formatter": "verbose",
        },
    },

    "loggers": {

        "django": {
            "handlers": [
                "console",
                "file"
            ],
            "level": "INFO",
            "propagate": False,
        },

        "django.db.backends": {
            "handlers": [
                "console"
            ],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


# ============================================================
# CLÉ PRIMAIRE PAR DÉFAUT
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"