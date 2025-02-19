"""
WSGI config for bug_tracker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

from core.environments import set_django_settings_module
from django.core.wsgi import get_wsgi_application

set_django_settings_module()

application = get_wsgi_application()
