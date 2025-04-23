import re

import pytest
from core.utils import bytes_to_mib, generate_username, get_file_extension, snake_to_title_case

pytestmark = pytest.mark.unit


def test_snake_to_title_case() -> None:
    assert snake_to_title_case("example_text") == "Example text"
    assert snake_to_title_case("alreadyformatted") == "Alreadyformatted"
    assert snake_to_title_case("with-hyphen_and_underscore") == "With hyphen and underscore"


def test_generate_username_default_prefix() -> None:
    username = generate_username()

    assert username.startswith("user_")
    assert len(username) == len("user_") + 8
    assert re.fullmatch(r"user_[0-9a-f]{8}", username)


def test_generate_username_custom_prefix() -> None:
    prefix = "guest_"

    username = generate_username(prefix)

    assert username.startswith(prefix)
    assert len(username) == len(prefix) + 8


def test_bytes_to_mib() -> None:
    assert bytes_to_mib(1048576) == 1.0  # 1 MiB
    assert bytes_to_mib(0) == 0.0
    assert bytes_to_mib(524288) == 0.5


def test_get_file_extension() -> None:
    assert get_file_extension("file.txt") == "txt"
    assert get_file_extension("archive.tar.gz") == "gz"
    assert get_file_extension(".hiddenfile") == ""
    assert get_file_extension("no_extension") == ""
