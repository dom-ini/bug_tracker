import pytest
from faker.proxy import Faker
from projects.models import Project
from rest_framework.test import APIClient, APIRequestFactory
from tests.factories import fake_project, fake_user
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
def request_factory() -> APIRequestFactory:
    factory = APIRequestFactory()
    factory.default_format = "json"
    return factory


@pytest.fixture
def password() -> str:
    return "StrongP@ssword1234!"


@pytest.fixture
def user_with_unverified_email(password: str) -> CustomUser:
    user = fake_user(password=password, is_verified=False)
    return user


@pytest.fixture
def user_with_verified_email(password: str) -> CustomUser:
    user = fake_user(password=password, is_verified=True)
    return user


@pytest.fixture
def project(user_with_verified_email: CustomUser) -> Project:
    return fake_project(user=user_with_verified_email)
