from typing import Sequence

import pytest
from core.exceptions import ApplicationException, custom_exception_handler
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import NotAcceptable

pytestmark = pytest.mark.unit


class DummyApplicationException(ApplicationException):
    message = "some class message"


def test_application_exception_sets_message() -> None:
    message = "some message"

    exc = ApplicationException(message)

    assert str(exc) == "some message"


def test_application_exception_subclass_sets_default_message() -> None:
    exc = DummyApplicationException()

    assert str(exc) == DummyApplicationException.message


def test_application_exception_subclass_overwrites_default_message_if_passed() -> None:
    message = "some message"

    exc = DummyApplicationException(message)

    assert str(exc) == message
    assert str(exc) != DummyApplicationException.message


@pytest.mark.parametrize(
    "exc,code",
    (
        (Http404(), status.HTTP_404_NOT_FOUND),
        (PermissionDenied(), status.HTTP_403_FORBIDDEN),
        (ValidationError(["Error 1"]), status.HTTP_400_BAD_REQUEST),
        (NotAcceptable(), status.HTTP_406_NOT_ACCEPTABLE),
    ),
)
def test_custom_exception_handler_handles_error(exc: Exception, code: int) -> None:
    response = custom_exception_handler(exc, {})

    assert response.status_code == code


@pytest.mark.parametrize(
    "exc",
    (
        Http404(),
        PermissionDenied(),
        ValidationError(["Error 1"]),
        NotAcceptable(),
    ),
)
def test_custom_exception_handler_contains_detail_field(exc: Exception) -> None:
    response = custom_exception_handler(exc, {})

    assert response.data.get("detail") is not None


@pytest.mark.parametrize("errors,key", ((["Error 1", "Error 2"], "non_field_errors"), ({"field1": "error"}, "field1")))
def test_custom_exception_handler_handles_errors_from_validation_error(errors: list | dict, key: str) -> None:
    exc = ValidationError(errors)

    response = custom_exception_handler(exc, {})

    assert isinstance(response.data["detail"][key], Sequence)
