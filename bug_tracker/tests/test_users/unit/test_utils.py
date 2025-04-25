import pytest
from django.utils.http import base36_to_int
from users.utils import user_id_to_url_str

pytestmark = pytest.mark.unit


def test_user_id_to_url_str_returns_base36_string() -> None:
    user_id = 123456
    result = user_id_to_url_str(user_id)

    assert isinstance(result, str)


@pytest.mark.parametrize("user_id", [0, 1, 42, 999999])
def test_user_id_to_url_str_with_various_ids(user_id: int) -> None:
    base36_str = user_id_to_url_str(user_id)

    assert isinstance(base36_str, str)
    assert base36_to_int(base36_str) == user_id
