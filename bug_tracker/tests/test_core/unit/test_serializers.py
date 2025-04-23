import pytest
from core.serializers import CommaSeparatedMultipleChoiceField, create_validation_error_for_field
from rest_framework.exceptions import ValidationError

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (["a", "b"], "a,b"),
        ([], ""),
    ],
)
def test_to_internal_value_returns_comma_joined_string(input_data: list[str], expected: str) -> None:
    field = CommaSeparatedMultipleChoiceField(choices=["a", "b", "c"])
    result = field.to_internal_value(input_data)

    assert result == expected


def test_to_internal_value_with_invalid_choice_raises_validation_error() -> None:
    field = CommaSeparatedMultipleChoiceField(choices=["a", "b", "c"])

    with pytest.raises(ValidationError):
        field.to_internal_value(["a", "x"])


def test_create_validation_error_for_field_returns_expected_error() -> None:
    error = create_validation_error_for_field("field", "This field is required.")

    assert isinstance(error, ValidationError)
    assert error.detail == {"field": ["This field is required."]}
