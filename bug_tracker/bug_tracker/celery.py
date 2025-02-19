import sys
from pathlib import Path

from celery import Celery
from core.environments import set_django_settings_module
from django.conf import settings

sys.path.append(str(Path(__file__).resolve().parent.parent))

app = Celery("bug_tracker")

set_django_settings_module()
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
