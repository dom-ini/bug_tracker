import os
from enum import Enum

from decouple import config


class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


def get_environment() -> str:
    return config("ENVIRONMENT", default=Environment.PRODUCTION.value)


def get_settings_module() -> str:
    environment = get_environment()
    settings_module = f"bug_tracker.settings.{environment}"
    return settings_module


def set_django_settings_module() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_settings_module())
