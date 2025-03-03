from typing import Any

from django import forms
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.forms import SetPasswordMixin
from django.utils.translation import gettext_lazy as _


class CustomSetPasswordForm(SetPasswordMixin, forms.Form):
    new_password = SetPasswordMixin.create_password_fields(label1=_("Password"), label2="")[0]

    def __init__(self, user: AbstractBaseUser, *args: Any, **kwargs: Any) -> None:
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        self.validate_password_for_user(self.user, "new_password")
        return super().clean()

    def save(self, commit: bool = True) -> AbstractBaseUser:
        return self.set_password_and_save(self.user, "new_password", commit=commit)
