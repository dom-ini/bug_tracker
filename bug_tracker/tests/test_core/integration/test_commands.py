import pytest
from django.core.management import call_command
from django.db import OperationalError, connections
from pytest_mock import MockerFixture

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_wait_for_db_ready(mocker: MockerFixture, capsys: pytest.CaptureFixture[str]) -> None:
    mocker.patch("core.management.commands.wait_for_db.get_default_db_connection", return_value=connections["default"])

    call_command("wait_for_db")

    captured = capsys.readouterr()
    assert "Waiting for database..." in captured.out
    assert "Database is ready!" in captured.out


@pytest.mark.django_db
def test_wait_for_db_retry_until_ready(mocker: MockerFixture, capsys: pytest.CaptureFixture[str]) -> None:
    get_conn_mock = mocker.Mock()
    get_conn_mock.side_effect = [OperationalError("DB down"), OperationalError("Still down"), connections["default"]]
    mocker.patch("core.management.commands.wait_for_db.get_default_db_connection", get_conn_mock)
    sleep_mock = mocker.patch("time.sleep", autospec=True)

    call_command("wait_for_db")

    captured = capsys.readouterr()
    assert "Waiting for database..." in captured.out
    assert captured.out.count("Database unavailable") == 2
    assert "Database is ready!" in captured.out
    assert sleep_mock.call_count == 2
