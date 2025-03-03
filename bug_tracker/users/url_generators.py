from allauth.account.utils import user_pk_to_url_str
from core.url_resolver import FrontendUrlType, resolve_front_url
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest


def generate_reset_password_url(_request: HttpRequest, user: AbstractBaseUser, key: str) -> str:
    url = f"{resolve_front_url(FrontendUrlType.RESET_PASSWORD)}/{user_pk_to_url_str(user)}/{key}"
    return url


def generate_email_confirmation_url(token: str) -> str:
    url = f"{resolve_front_url(FrontendUrlType.VERIFY_EMAIL)}/{token}"
    return url
