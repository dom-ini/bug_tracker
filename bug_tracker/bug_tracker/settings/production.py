from .base import *
from .base import REST_AUTH, STORAGES

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

REST_AUTH.update(
    {
        "JWT_AUTH_HTTPONLY": True,
        "JWT_AUTH_SECURE": True,
    }
)

CORE_EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

MEDIA_URL = "https://media.bugtracker.com/"
STORAGES.update(
    {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
    }
)
