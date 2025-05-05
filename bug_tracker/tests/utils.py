from django.core import mail
from django.urls import reverse
from django.views import View
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory
from users.models import CustomUser


def clear_outbox() -> None:
    mail.outbox.clear()


def check_views_require_authentication(
    *, url_name: str, kwargs: dict[str, int], method: str, view_class: type[View], request_factory: APIRequestFactory
) -> None:
    url = reverse(url_name, kwargs=kwargs)

    request = getattr(request_factory, method)(url)
    response = view_class.as_view()(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def login_as(*, client: APIClient, user: CustomUser, password: str) -> None:
    login_url = reverse("rest_login")
    login_data = {
        "username": user.username,
        "password": password,
    }
    response = client.post(login_url, data=login_data)
    assert response.status_code == status.HTTP_200_OK, "Login failed"
    token = response.data["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
