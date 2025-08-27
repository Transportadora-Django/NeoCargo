"""
Development settings for frete_proj project.
Settings specific to development environment.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database - SQLite for development
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
