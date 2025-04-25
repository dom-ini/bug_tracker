import pytest
from users.url_generators import generate_email_confirmation_url, generate_reset_password_url
from users.utils import user_id_to_url_str

pytestmark = pytest.mark.unit


def test_generate_reset_password_url_contains_key_and_user_id() -> None:
    user_id = 1
    key = "key"

    url = generate_reset_password_url(user_id=user_id, key=key)

    url_segments = url.split("/")
    assert key in url_segments
    assert user_id_to_url_str(user_id) in url_segments


def test_generate_email_confirmation_url_contains_token() -> None:
    token = "token"

    url = generate_email_confirmation_url(token)

    assert token in url.split("/")
