"""
Production settings for frete_proj project.
Settings specific to production environment.
"""

import os

import dj_database_url

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Configuração de ALLOWED_HOSTS mais flexível para Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, "localhost", "127.0.0.1"]
elif os.getenv("ALLOWED_HOSTS"):
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
else:
    ALLOWED_HOSTS = ["*"]  # Fallback mais permissivo

# Database - PostgreSQL for production
DATABASES = {"default": dj_database_url.parse(os.getenv("DATABASE_URL", "sqlite:///db.sqlite3"))}

# Configurações de conexão mais resilientes para Render
DATABASES["default"]["CONN_MAX_AGE"] = 0  # Não reutilizar conexões (mais seguro)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # Django 4.1+ health checks
DATABASES["default"]["OPTIONS"] = {
    "connect_timeout": 10,
    "options": "-c statement_timeout=30000",  # 30 segundos timeout
}

# WhiteNoise configuration for production - Mais resiliente
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_MAX_AGE = 31536000  # 1 year cache
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
    "zip",
    "gz",
    "tgz",
    "bz2",
    "tbz",
    "xz",
    "br",
]

# Configuração mais resiliente para arquivos estáticos ausentes
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = False

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Configurações SSL mais flexíveis para Render
if not DEBUG:
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False").lower() == "true"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Session security
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() == "true"
    CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "True").lower() == "true"

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
USE_TZ = True

# Email configuration for production (Mailgun)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.mailgun.org")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")  # postmaster@seu-dominio.mailgun.org
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")  # Senha SMTP do Mailgun
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "NeoCargo <noreply@seu-dominio.mailgun.org>")
SERVER_EMAIL = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

# Logging configuration otimizado para produção
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "gunicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
