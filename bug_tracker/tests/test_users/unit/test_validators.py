import pytest
from django.core.exceptions import ValidationError
from users.validators import RepeatingCharactersPasswordValidator, RequiredCharactersPasswordValidator

pytestmark = pytest.mark.unit


class TestRequiredCharactersPasswordValidator:
    @pytest.fixture
    def validator(self) -> RequiredCharactersPasswordValidator:
        return RequiredCharactersPasswordValidator()

    def test_valid_password_passes(self, validator: RequiredCharactersPasswordValidator) -> None:
        validator.validate("StrongP@ssw0rd")

    @pytest.mark.parametrize(
        "password",
        [
            "nopunctuation1A",
            "NOLOWER1!",
            "noupper1!",
            "NoNumber!",
        ],
    )
    def test_invalid_password_raises(self, validator: RequiredCharactersPasswordValidator, password: str) -> None:
        with pytest.raises(ValidationError):
            validator.validate(password)

    def test_completely_invalid_password_raises_multiple_reasons(
        self, validator: RequiredCharactersPasswordValidator
    ) -> None:
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("password")

        message = str(exc_info.value)
        assert "uppercase" in message
        assert "digit" in message
        assert "special" in message


class TestRepeatingCharactersPasswordValidator:
    @pytest.fixture
    def validator(self) -> RepeatingCharactersPasswordValidator:
        return RepeatingCharactersPasswordValidator(max_repeating=2)

    def test_valid_password_with_no_repeating_characters(self, validator: RepeatingCharactersPasswordValidator) -> None:
        validator.validate("Aa11!!bb")

    def test_valid_password_with_max_repeating_characters(
        self, validator: RepeatingCharactersPasswordValidator
    ) -> None:
        validator.validate("aaBB11!!")

    def test_invalid_password_with_excessive_repeats(self, validator: RepeatingCharactersPasswordValidator) -> None:
        with pytest.raises(ValidationError):
            validator.validate("aaaBBB")

    def test_custom_max_repeating(self) -> None:
        validator = RepeatingCharactersPasswordValidator(max_repeating=1)
        with pytest.raises(ValidationError):
            validator.validate("aa")

    def test_help_text_reflects_max_repeating(self) -> None:
        validator = RepeatingCharactersPasswordValidator(max_repeating=3)
        help_text = validator.get_help_text()
        assert "3" in help_text
