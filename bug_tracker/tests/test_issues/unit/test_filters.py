from unittest.mock import Mock

import pytest
from issues.filters import HistoryEntryFilter
from issues.models import HistoryEntrySubject
from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


@pytest.fixture
def filter_value() -> str:
    return HistoryEntrySubject.ISSUE


@pytest.fixture
def mock_content_type(mocker: MockerFixture) -> Mock:
    return mocker.Mock()


@pytest.fixture
def filters(filter_value: str, mock_content_type: Mock) -> HistoryEntryFilter:
    class TestHistoryEntryFilter(HistoryEntryFilter):
        subject_to_ct = {filter_value: mock_content_type}

    return TestHistoryEntryFilter()


def test_history_entry_filter_filter_subject(
    mocker: MockerFixture, filters: HistoryEntryFilter, filter_value: str, mock_content_type: Mock
) -> None:
    mock_queryset = mocker.Mock()

    filters.filter_subject(queryset=mock_queryset, _name="name", value=filter_value)

    mock_queryset.filter.assert_called_once_with(content_type=mock_content_type)


def test_history_entry_filter_filter_subject_value_none(mocker: MockerFixture, filters: HistoryEntryFilter) -> None:
    mock_queryset = mocker.Mock()

    filtered = filters.filter_subject(queryset=mock_queryset, _name="name", value=None)

    assert filtered is mock_queryset
