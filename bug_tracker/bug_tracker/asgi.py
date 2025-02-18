"""
ASGI config for bug_tracker project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

from django.core.asgi import get_asgi_application

from bug_tracker.environments import set_django_settings_module

set_django_settings_module()

application = get_asgi_application()
