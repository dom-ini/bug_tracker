import pytest
from django.conf import settings
from django.http import HttpRequest
from projects.project_resolver import MissingProjectIdentifierHeader, resolve_project_from_header
from pytest_mock import MockerFixture
from tests.factories import fake_project
from users.models import CustomUser

pytestmark = pytest.mark.unit


@pytest.mark.django_db
def test_resolve_project_from_header_should_return_project_when_valid_subdomain(
    mocker: MockerFixture, user_with_verified_email: CustomUser
) -> None:
    request = HttpRequest()
    request.META = {f"HTTP_{settings.SUBDOMAIN_HEADER_NAME}": "test-subdomain"}
    request.user = mocker.Mock()
    expected_project = fake_project(user=user_with_verified_email)
    mocker.patch("projects.project_resolver.project_get_by_subdomain", return_value=expected_project)

    project = resolve_project_from_header(request)

    assert project == expected_project


def test_resolve_project_from_header_should_raise_exception_when_header_is_missing() -> None:
    request = HttpRequest()

    with pytest.raises(MissingProjectIdentifierHeader):
        resolve_project_from_header(request)


@pytest.mark.django_db
def test_resolve_project_from_header_should_return_none_when_project_not_found(mocker: MockerFixture) -> None:
    request = HttpRequest()
    request.META = {f"HTTP_{settings.SUBDOMAIN_HEADER_NAME}": "nonexistent-subdomain"}
    request.user = mocker.Mock()
    mocker.patch("projects.project_resolver.project_get_by_subdomain", return_value=None)

    project = resolve_project_from_header(request)

    assert project is None
