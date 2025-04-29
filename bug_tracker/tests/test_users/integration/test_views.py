from types import SimpleNamespace
from typing import Callable

import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory
from users.models import CustomUser
from users.views import CustomPasswordResetView, CustomRegisterView, CustomResendEmailVerificationView

pytestmark = pytest.mark.integration


@pytest.fixture
def throttle_email_views(settings: SimpleNamespace) -> None:
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["email"] = "0/minute"


@pytest.fixture
def disable_email_views_throttling(settings: SimpleNamespace) -> None:
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["email"] = "100/minute"


@pytest.mark.django_db
def test_register_view_invalid_password(request_factory: APIRequestFactory) -> None:
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "weak",
        "first_name": "Test",
        "last_name": "User",
    }

    request = request_factory.post(reverse("register"), data=data)
    view = CustomRegisterView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name,view",
    [
        ("resend_email", CustomResendEmailVerificationView.as_view()),
        ("password_reset", CustomPasswordResetView.as_view()),
    ],
)
@pytest.mark.usefixtures("disable_email_views_throttling")
def test_views_send_emails_correctly(
    user_with_unverified_email: CustomUser, url_name: str, view: Callable, request_factory: APIRequestFactory
) -> None:
    data = {
        "email": user_with_unverified_email.email,
    }

    request = request_factory.post(reverse(url_name), data=data)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 1


@pytest.mark.django_db
@pytest.mark.usefixtures("throttle_email_views")
def test_register_view_throttling(request_factory: APIRequestFactory) -> None:
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "StrongP@ssw0rd",
        "first_name": "Test",
        "last_name": "User",
    }

    request = request_factory.post(reverse("register"), data)
    view = CustomRegisterView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
@pytest.mark.usefixtures("throttle_email_views")
def test_password_reset_view_throttling(request_factory: APIRequestFactory) -> None:
    data = {
        "email": "test@example.com",
    }

    request = request_factory.post(reverse("password_reset"), data)
    view = CustomPasswordResetView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
@pytest.mark.usefixtures("throttle_email_views")
def test_resend_verification_email_view_throttling(request_factory: APIRequestFactory) -> None:
    data = {
        "email": "test@example.com",
    }

    request = request_factory.post(reverse("resend_email"), data)
    view = CustomResendEmailVerificationView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
