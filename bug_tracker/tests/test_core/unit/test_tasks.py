from unittest.mock import MagicMock

import pytest
from celery.exceptions import Reject
from core.tasks import async_send_messages
from django.core.mail import EmailMessage
from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_get_connection(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("core.tasks.get_connection")


@pytest.fixture
def invalid_email_data() -> dict[str, str]:
    return {"invalid": "invalid"}


@pytest.fixture
def valid_email_data() -> dict[str, str]:
    return {
        "subject": "subject",
        "body": "body",
        "from_email": "from_email@example.com",
        "to": ["to_email@example.com"],
    }


def test_async_send_messages_rejects_on_incorrect_email_data(invalid_email_data: dict[str, str]) -> None:
    with pytest.raises(Reject):
        async_send_messages(invalid_email_data)


def test_async_send_messages_sends_emails_message_instances_to_email_backend(
    mock_get_connection: MagicMock, valid_email_data: dict[str, str]
) -> None:
    async_send_messages([valid_email_data])

    send_messages = mock_get_connection.return_value.send_messages
    email = send_messages.call_args[0][0][0]
    assert isinstance(email, EmailMessage)
    send_messages.assert_called_once()
