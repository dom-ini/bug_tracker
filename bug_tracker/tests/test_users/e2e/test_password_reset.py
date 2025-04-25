import re

import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser

pytestmark = pytest.mark.e2e


@pytest.mark.django_db
def test_password_reset_flow(client: APIClient, user_with_verified_email: CustomUser) -> None:
    email = user_with_verified_email.email
    reset_url = reverse("password_reset")
    response = client.post(reset_url, {"email": email})

    assert response.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 1
    reset_email = mail.outbox[0]
    assert email in reset_email.to

    generated_reset_url = re.search(r"https?://[^/]+(?:/[^/]+)*/([a-zA-Z0-9]+)/([a-zA-Z0-9\-]+)", reset_email.body)
    assert generated_reset_url is not None, "No reset key found in email"
    uid, token = generated_reset_url.groups()

    confirm_url = reverse("rest_password_reset_confirm")
    new_password = "NewStrongPass456!"
    response = client.post(
        confirm_url,
        {
            "uid": uid,
            "token": token,
            "new_password": new_password,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    login_url = reverse("rest_login")
    response = client.post(
        login_url,
        {
            "username": user_with_verified_email.username,
            "password": new_password,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
