import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser

pytestmark = pytest.mark.e2e


@pytest.mark.django_db
def test_login_success(client: APIClient, user_with_verified_email: CustomUser, password: str) -> None:
    payload = {
        "username": user_with_verified_email.username,
        "password": password,
    }

    response = client.post(reverse("rest_login"), data=payload)

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_unverified_email_should_fail(
    client: APIClient, user_with_unverified_email: CustomUser, password: str
) -> None:
    payload = {
        "username": user_with_unverified_email.username,
        "password": password,
    }

    response = client.post(reverse("rest_login"), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_invalid_password_should_fail(client: APIClient, user_with_verified_email: CustomUser) -> None:
    payload = {
        "username": user_with_verified_email.username,
        "password": "invalid",
    }

    response = client.post(reverse("rest_login"), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_user_not_registered_should_fail(client: APIClient) -> None:
    payload = {
        "username": "email@example.com",
        "password": "password",
    }

    response = client.post(reverse("rest_login"), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
