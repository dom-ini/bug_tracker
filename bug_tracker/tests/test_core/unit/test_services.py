from typing import Any

import pytest
from core.services import query_or_404
from django.http import Http404

pytestmark = pytest.mark.unit


def test_query_or_404_returns_object() -> None:
    expected = {"id": 1, "name": "test"}

    def selector() -> dict[str, Any]:
        return expected

    result = query_or_404(selector)

    assert result == expected


def test_query_or_404_raises_http404_on_none() -> None:
    def selector():
        return None

    with pytest.raises(Http404):
        query_or_404(selector)


def test_query_or_404_passes_arguments_to_selector() -> None:
    def selector(a: str, b: str | None = None) -> bool | None:
        if a == "expected" and b == "value":
            return True
        return None

    result = query_or_404(selector, a="expected", b="value")

    assert result is True
