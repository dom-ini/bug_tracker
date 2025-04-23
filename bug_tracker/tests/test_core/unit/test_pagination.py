import pytest
from core.pagination import LimitOffsetPagination
from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_limit_offset_pagination_response_format(mocker: MockerFixture) -> None:
    limit, offset, count = 10, 0, 100
    pagination = LimitOffsetPagination()
    pagination.limit = limit
    pagination.offset = offset
    pagination.count = count
    pagination.request = mocker.Mock()

    data = [{"name": "test"}]
    response = pagination.get_paginated_response(data)

    assert response.data["limit"] == limit
    assert response.data["offset"] == offset
    assert response.data["count"] == count
    assert response.data["results"] == data
    assert "next" in response.data
    assert "previous" in response.data
