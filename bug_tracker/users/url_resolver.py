from allauth.account.utils import user_pk_to_url_str
from django.http import HttpRequest
from users.models import CustomUser

from bug_tracker.url_resolver import FrontendUrlType, resolve_front_url


def generate_reset_password_url(_request: HttpRequest, user: CustomUser, key: str) -> str:
    url = f"{resolve_front_url(FrontendUrlType.RESET_PASSWORD)}/{user_pk_to_url_str(user)}/{key}"
    return url


def generate_email_confirmation_url(token: str) -> str:
    url = f"{resolve_front_url(FrontendUrlType.VERIFY_EMAIL)}/{token}"
    return url
