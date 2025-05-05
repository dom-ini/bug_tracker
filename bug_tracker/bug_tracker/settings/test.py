from .base import *
from .base import REST_AUTH, STORAGES

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

REST_AUTH.update(
    {
        "JWT_AUTH_HTTPONLY": False,
        "JWT_AUTH_SECURE": False,
    }
)

CORE_EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

MEDIA_URL = "http://media.bugtracker.local/"
STORAGES.update(
    {
        "default": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
    }
)
