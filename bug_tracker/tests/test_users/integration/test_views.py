from types import SimpleNamespace

import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.fixture
def throttle_email_views(settings: SimpleNamespace) -> None:
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["email"] = "0/minute"


@pytest.fixture
def disable_email_views_throttling(settings: SimpleNamespace) -> None:
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["email"] = "100/minute"


@pytest.mark.django_db
def test_register_view_success(client: APIClient) -> None:
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "StrongP@ssw0rd",
        "first_name": "Test",
        "last_name": "User",
    }

    response = client.post(reverse("register"), data)

    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(email="test@example.com").exists()
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_register_view_invalid_password(client: APIClient) -> None:
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "weak",
        "first_name": "Test",
        "last_name": "User",
    }

    response = client.post(reverse("register"), data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["resend_email", "password_reset"])
@pytest.mark.usefixtures("disable_email_views_throttling")
def test_views_send_emails_correctly(user_with_unverified_email: CustomUser, url_name: str, client: APIClient) -> None:
    data = {
        "email": user_with_unverified_email.email,
    }

    response = client.post(reverse(url_name), data)

    assert response.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 1


@pytest.mark.django_db
@pytest.mark.usefixtures("throttle_email_views")
def test_register_view_throttling(client: APIClient) -> None:
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "StrongP@ssw0rd",
        "first_name": "Test",
        "last_name": "User",
    }

    response = client.post(reverse("register"), data)

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
@pytest.mark.usefixtures("throttle_email_views")
def test_password_reset_view_throttling(client: APIClient) -> None:
    data = {
        "email": "test@example.com",
    }

    response = client.post(reverse("password_reset"), data)

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
@pytest.mark.usefixtures("throttle_email_views")
def test_resend_verification_email_view_throttling(client: APIClient) -> None:
    data = {
        "email": "test@example.com",
    }

    response = client.post(reverse("resend_email"), data)

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
