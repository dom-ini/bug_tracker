from unittest.mock import MagicMock

import pytest
from core.middleware import LogIpMiddleware, get_client_ip
from django.http import HttpRequest
from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_request() -> HttpRequest:
    return HttpRequest()


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("core.middleware.get_main_logger")


@pytest.mark.parametrize(
    "meta_data, expected_ip",
    [
        ({"HTTP_X_FORWARDED_FOR": "192.168.1.1, 10.0.0.1"}, "192.168.1.1"),
        ({"REMOTE_ADDR": "10.0.0.2"}, "10.0.0.2"),
        ({}, "Unknown"),
    ],
)
def test_get_client_ip(mock_request: HttpRequest, meta_data: dict[str, str], expected_ip: str) -> None:
    mock_request.META = meta_data
    assert get_client_ip(mock_request) == expected_ip


@pytest.mark.parametrize("ip,user", [("192.168.1.30", MagicMock(username="user")), ("10.0.0.2", None)])
def test_log_ip_middleware_logs_ip(
    mock_logger: MagicMock, mock_request: HttpRequest, ip: str, user: MagicMock | None
) -> None:
    get_response = MagicMock()
    mock_request.user = user
    mock_request.META["REMOTE_ADDR"] = ip
    middleware = LogIpMiddleware(get_response)

    response = middleware(mock_request)
    logged_message = mock_logger.return_value.info.call_args[0][0]

    assert response == get_response.return_value
    assert ip in logged_message
    assert str(user) in logged_message
