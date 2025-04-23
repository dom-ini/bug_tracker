import pytest
from core.pagination import LimitOffsetPagination, get_paginated_response
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

pytestmark = pytest.mark.integration


class DummyObject:
    def __init__(self, name: str):
        self.name = name


class DummySerializer(serializers.Serializer):
    name = serializers.CharField()


class DummyView(APIView):
    pass


@pytest.fixture
def dummy_data() -> list[DummyObject]:
    return [DummyObject(name=f"Item {i}") for i in range(1, 21)]


def test_get_paginated_response_with_pagination(dummy_data: list[DummyObject]) -> None:
    limit = 5
    offset = 0
    factory = APIRequestFactory()
    request = factory.get(f"/fake-url/?limit={limit}&offset={offset}")

    view = DummyView()
    response = get_paginated_response(
        pagination_class=LimitOffsetPagination,
        serializer_class=DummySerializer,
        queryset=dummy_data,
        request=Request(request),
        view=view,
    )

    assert response.status_code == 200
    assert "results" in response.data
    assert len(response.data["results"]) == limit
    assert response.data["count"] == len(dummy_data)
    assert response.data["limit"] == limit
    assert response.data["offset"] == offset


def test_get_paginated_response_without_pagination(dummy_data: list[DummyObject]) -> None:
    limit = 1000
    factory = APIRequestFactory()
    request = factory.get(f"/fake-url/?limit={limit}")

    view = DummyView()
    paginator = LimitOffsetPagination()
    paginator.max_limit = limit

    response = get_paginated_response(
        pagination_class=type(paginator),
        serializer_class=DummySerializer,
        queryset=dummy_data,
        request=Request(request),
        view=view,
    )

    assert response.status_code == 200
    assert len(response.data["results"]) == len(dummy_data)
