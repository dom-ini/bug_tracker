from enum import Enum

from django.conf import settings


class FrontendUrlType(str, Enum):
    BASE = "BASE"
    RESET_PASSWORD = "RESET_PASSWORD"
    VERIFY_EMAIL = "VERIFY_EMAIL"


def resolve_front_url(url_type: FrontendUrlType | str, include_protocol: bool = True) -> str:
    if url_type not in settings.FRONTEND_URLS:
        raise ValueError(f"{url_type} is not defined in settings.FRONTEND_URLS")
    url = f"{'https://' if include_protocol else ''}{settings.FRONTEND_URLS[url_type]}"
    if url_type == FrontendUrlType.BASE:
        return url
    return f"{settings.FRONTEND_URLS[FrontendUrlType.BASE]}/{url}"
