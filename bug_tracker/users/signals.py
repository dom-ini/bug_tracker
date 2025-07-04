from typing import Any

from axes.signals import user_locked_out
from django.dispatch import receiver
from rest_framework.exceptions import PermissionDenied


@receiver(user_locked_out)
def raise_permission_denied(*_args: Any, **_kwargs: Any) -> None:
    raise PermissionDenied("Too many failed login attempts")
