import pytest
from core.filters import BaseOrdering

pytestmark = pytest.mark.unit


class DummyOrdering(BaseOrdering):
    base_fields = ("created_at", "title")


def test_ordering_fields() -> None:
    expected = [
        ("created_at", "Created at"),
        ("-created_at", "Created at (descending)"),
        ("title", "Title"),
        ("-title", "Title (descending)"),
    ]

    assert DummyOrdering.fields == expected
