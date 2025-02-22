import pytest
from core.url_resolver import FrontendUrlType, resolve_front_url
from django.conf import Settings, settings

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def override_frontend_urls(settings: Settings) -> None:
    settings.FRONTEND_URLS = {
        FrontendUrlType.BASE: "https://example.com",
        FrontendUrlType.RESET_PASSWORD: "/reset-password",
    }


def test_resolve_url_base() -> None:
    resolved = resolve_front_url(FrontendUrlType.BASE)

    assert resolved == settings.FRONTEND_URLS.get(FrontendUrlType.BASE)
    assert not resolved.endswith("/")


def test_resolve_url_other() -> None:
    base = settings.FRONTEND_URLS.get(FrontendUrlType.BASE)
    reset_password = settings.FRONTEND_URLS.get(FrontendUrlType.RESET_PASSWORD)

    resolved = resolve_front_url(FrontendUrlType.RESET_PASSWORD)

    assert resolved == f"{base}/{reset_password}"


def test_resolve_url_invalid_url_type_should_fail() -> None:
    with pytest.raises(ValueError):
        resolve_front_url("non-existing-url")
