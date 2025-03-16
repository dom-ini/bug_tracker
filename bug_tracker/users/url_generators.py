from core.url_resolver import FrontendUrlType, resolve_front_url
from django.contrib.auth.base_user import AbstractBaseUser
from requests import Request
from users.utils import user_id_to_url_str


def generate_reset_password_url(user_id: int, key: str) -> str:
    url = f"{resolve_front_url(FrontendUrlType.RESET_PASSWORD)}/{user_id_to_url_str(user_id)}/{key}"
    return url


def generate_allauth_reset_password_url(_request: Request, user: AbstractBaseUser, key: str) -> str:
    return generate_reset_password_url(user_id=user.pk, key=key)


def generate_email_confirmation_url(token: str) -> str:
    url = f"{resolve_front_url(FrontendUrlType.VERIFY_EMAIL)}/{token}"
    return url
