import itertools
from typing import Any

from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

_SPECIAL_CHARS = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

username_validators = [ASCIIUsernameValidator()]


class RequiredCharactersPasswordValidator:
    def validate(self, password: str, *_args: Any) -> None:
        errors: list[str] = []

        if not any(c.islower() for c in password):
            errors.append(_("at least one lowercase letter"))
        if not any(c.isupper() for c in password):
            errors.append(_("at least one uppercase letter"))
        if not any(c.isdigit() for c in password):
            errors.append(_("at least one digit"))
        if not any(c in _SPECIAL_CHARS for c in password):
            errors.append(_("at least one special character"))

        if errors:
            raise ValidationError(
                _("This password must contain: ") + ", ".join(errors) + ".",
                code="password_missing_required_characters",
            )

    def get_help_text(self) -> str:
        return _(
            (
                "Your password must include at least one lowercase letter, one uppercase letter, "
                "one digit and one special character."
            )
        )


class RepeatingCharactersPasswordValidator:
    def __init__(self, max_repeating: int = 2) -> None:
        self.max_repeating = max_repeating

    def _has_excessive_repeating_characters(self, password: str) -> bool:
        for _char, group in itertools.groupby(password):
            if sum(1 for _elem in group) > self.max_repeating:
                return True
        return False

    def validate(self, password: str, *_args: Any) -> None:
        if self._has_excessive_repeating_characters(password):
            raise ValidationError(
                _("This password must not contain more than %(max_repeating)d repeating characters in a row.")
                % {"max_repeating": self.max_repeating},
            )

    def get_help_text(self) -> str:
        return _("Your password should contain no more than %(max_repeating)d repeating characters.") % {
            "max_repeating": self.max_repeating
        }
