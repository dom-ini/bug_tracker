import os
from typing import Callable
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from core.environments import Environment, get_environment, get_settings_module, set_django_settings_module
from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


SetEnvFunc = Callable[[str], None]


@pytest.fixture
def set_env(monkeypatch: MonkeyPatch) -> SetEnvFunc:
    def _set_env(env_value: str) -> None:
        monkeypatch.setenv("ENVIRONMENT", env_value)

    return _set_env


@pytest.fixture
def mock_config(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("core.environments.config")


def test_get_environment_default(mock_config: MagicMock) -> None:
    mock_config.return_value = Environment.PRODUCTION.value

    assert get_environment() == Environment.PRODUCTION


def test_get_environment_custom(set_env: SetEnvFunc) -> None:
    set_env(Environment.DEVELOPMENT.value)

    assert get_environment() == Environment.DEVELOPMENT


@pytest.mark.parametrize("env_value", [Environment.PRODUCTION.value, Environment.DEVELOPMENT.value])
def test_get_settings_module(set_env: SetEnvFunc, env_value: str) -> None:
    set_env(env_value)

    settings_module = f"bug_tracker.settings.{env_value}"
    assert get_settings_module() == settings_module


def test_set_django_settings_module(mocker: MockerFixture) -> None:
    settings_module = "some.settings.module"
    mocker.patch("core.environments.get_settings_module", return_value=settings_module)
    os.environ.pop("DJANGO_SETTINGS_MODULE", None)

    set_django_settings_module()

    assert os.environ.get("DJANGO_SETTINGS_MODULE") == settings_module
