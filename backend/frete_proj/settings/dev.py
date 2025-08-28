"""
Development settings for frete_proj project.
Settings specific to development environment.
"""

import os
import dj_database_url
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

# Database - PostgreSQL for Docker, SQLite for local development
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # Using PostgreSQL (Docker environment)
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Using SQLite (Local development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Development specific apps
INSTALLED_APPS += [
    # Add development specific apps here
    # 'debug_toolbar',  # Uncomment when needed
]

# Development specific middleware
MIDDLEWARE += [
    # Add development specific middleware here
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',  # Uncomment when needed
]

# Development specific settings
# Email configuration - MailHog for Docker, console for local development
EMAIL_HOST = os.getenv('EMAIL_HOST')
if EMAIL_HOST:
    # Using MailHog (Docker environment)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'mailhog')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '1025'))
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
    EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@neocargo.local')
else:
    # Using console backend (Local development)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Internal IPs for debug toolbar (when used)
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Logging configuration for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
