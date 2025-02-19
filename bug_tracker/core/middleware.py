from typing import Callable

from core.logger import get_main_logger
from django.http import HttpRequest, HttpResponse


def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR", "Unknown")


class LogIpMiddleware:
    """Middleware to log IP address of incoming HTTP requests."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response: HttpResponse = self.get_response(request)
        ip = get_client_ip(request)
        user = request.user
        get_main_logger().info(f"Request from IP: {ip}, user: {user}")
        return response
