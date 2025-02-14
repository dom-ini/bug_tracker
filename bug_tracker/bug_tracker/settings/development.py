from .base import *
from .base import REST_AUTH

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

REST_AUTH.update(
    {
        "JWT_AUTH_HTTPONLY": False,
        "JWT_AUTH_SECURE": False,
    }
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
