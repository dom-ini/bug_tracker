import pytest
from allauth.account.models import EmailAddress
from faker.proxy import Faker
from rest_framework.test import APIClient
from users.models import CustomUser


@pytest.fixture
def faker() -> Faker:
    fake = Faker()
    return fake


@pytest.fixture
def client() -> APIClient:
    api_client = APIClient()
    api_client.default_format = "json"
    return api_client


@pytest.fixture
def password() -> str:
    return "StrongP@ssword1234!"


@pytest.fixture
def user(password: str) -> CustomUser:
    return CustomUser.objects.create_user(username="user", email="user@example.com", password=password)


@pytest.fixture
def user_with_unverified_email(user: CustomUser) -> CustomUser:
    EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)
    return user


@pytest.fixture
def user_with_verified_email(user: CustomUser) -> CustomUser:
    EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
    return user
