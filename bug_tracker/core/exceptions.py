from typing import Any

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler


class ApplicationException(Exception):
    message: str = ""

    def __init__(self, message: str = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)


class Conflict(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("Conflict with existing resource.")
    default_code = "conflict"


class Unprocessable(exceptions.APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = _("Could not process the request.")
    default_code = "unprocessable_entity"


def custom_exception_handler(exc: Any, ctx: Any) -> Response | None:
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, ctx)

    if response is None:
        return response

    if isinstance(exc.detail, (list, dict)):
        response.data = {"detail": response.data}

    return response
