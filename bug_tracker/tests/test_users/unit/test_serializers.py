from typing import Callable

import pytest
from django.core.exceptions import ValidationError
from users.serializers import CustomPasswordResetSerializer, CustomRegisterSerializer

pytestmark = pytest.mark.unit


@pytest.mark.django_db
def test_register_serializer_get_cleaned_data() -> None:
    data = {
        "username": "user1",
        "email": "user1@example.com",
        "first_name": "First",
        "last_name": "Last",
        "password": "StrongP@ssword123",
    }

    serializer = CustomRegisterSerializer(data=data)

    assert serializer.is_valid()
    cleaned_data = serializer.get_cleaned_data()
    assert cleaned_data["username"] == data["username"]
    assert cleaned_data["email"] == data["email"]
    assert cleaned_data["first_name"] == data["first_name"]
    assert cleaned_data["last_name"] == data["last_name"]
    assert cleaned_data["password"] == data["password"]


def test_register_serializer_validate_email_should_pass() -> None:
    serializer = CustomRegisterSerializer()
    valid_email = "valid@example.com"

    validated = serializer.validate_email(valid_email)

    assert validated == valid_email


def test_register_serializer_validate_password_should_pass_with_strong_password() -> None:
    serializer = CustomRegisterSerializer()
    valid_password = "StrongP@ssword123"

    validated = serializer.validate_password(valid_password)
    assert validated == valid_password


def test_register_serializer_validate_password_should_fail_with_weak_password() -> None:
    serializer = CustomRegisterSerializer()
    invalid_password = "weak"

    with pytest.raises(ValidationError):
        serializer.validate_password(invalid_password)


def test_password_reset_serializer_get_email_options_contains_url_generator() -> None:
    serializer = CustomPasswordResetSerializer()

    email_opts = serializer.get_email_options()

    url_generator = email_opts["url_generator"]
    assert url_generator is not None
    assert isinstance(url_generator, Callable)
