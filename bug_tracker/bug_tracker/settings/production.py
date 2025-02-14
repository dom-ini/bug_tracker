from .base import *
from .base import REST_AUTH

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = True

REST_AUTH.update(
    {
        "JWT_AUTH_HTTPONLY": True,
        "JWT_AUTH_SECURE": True,
    }
)
