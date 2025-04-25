import re

import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.e2e


@pytest.mark.django_db
def test_user_registration_and_email_verification(client: APIClient) -> None:
    username = "testuser"
    email = "testuser@example.com"
    password = "StrongP@ssword1"
    user_data = {
        "email": email,
        "username": username,
        "password": password,
        "first_name": "Test",
        "last_name": "User",
    }
    register_url = reverse("register")

    response = client.post(register_url, user_data)

    assert response.status_code == 201
    assert len(mail.outbox) == 1
    verification_email = mail.outbox[0]
    assert email in verification_email.to

    match = re.search(r"https?://[^/]+(?:/[^/]+)*/([a-zA-Z0-9\-:_.'=+]+)", verification_email.body)
    assert match, "No confirmation link found in email body"
    token = match.groups()[0]

    verify_url = reverse("rest_verify_email")
    confirm_response = client.post(verify_url, data={"key": token})
    assert confirm_response.status_code == 200

    login_url = reverse("rest_login")
    response = client.post(
        login_url,
        {
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
