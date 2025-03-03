from typing import Any, Protocol

from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import setup_user_email
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
)
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest
from rest_framework import serializers
from users.forms import CustomSetPasswordForm
from users.url_generators import generate_reset_password_url


class HasCleanedDataT(Protocol):
    cleaned_data: dict[str, Any]


class AccountAdapterT(Protocol):
    def clean_password(self, password: str) -> str: ...

    def clean_email(self, email: str) -> str: ...

    def send_account_already_exists_mail(self, email: str) -> None: ...

    def send_notification_mail(self, template_prefix: str, user: AbstractBaseUser) -> None: ...

    def new_user(self, request: HttpRequest) -> AbstractBaseUser: ...

    def save_user(
        self,
        request: HttpRequest,
        user: AbstractBaseUser,
        form: HasCleanedDataT,
        commit: bool,
    ) -> AbstractBaseUser: ...


class CustomRegisterSerializer(RegisterSerializer):
    password1 = None
    password2 = None
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cleaned_data: dict[str, Any] = {}
        self.adapter: AccountAdapterT = get_adapter()

    def get_cleaned_data(self) -> dict[str, str]:
        return {
            "username": self.validated_data.get("username", ""),
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "password": self.validated_data.get("password", ""),
        }

    def validate[DataT](self, data: DataT) -> DataT:
        return data

    def validate_password(self, password: str) -> str:
        return self.adapter.clean_password(password)

    def validate_email(self, email: str) -> str:
        return self.adapter.clean_email(email)

    def _check_email_already_used(self, email: str) -> bool:
        return email and EmailAddress.objects.is_verified(email)

    def save(self, request: HttpRequest) -> AbstractBaseUser | None:
        self.cleaned_data = self.get_cleaned_data()
        email = self.cleaned_data.get("email", "")

        if self._check_email_already_used(email):
            self.adapter.send_account_already_exists_mail(email)
            return None

        user = self.adapter.new_user(request)
        user = self.adapter.save_user(request, user, self, commit=False)
        user.save()
        setup_user_email(request, user, [])
        return user


class CustomLoginSerializer(LoginSerializer):
    email = None


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self) -> dict[str, Any]:
        return {"url_generator": generate_reset_password_url}


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    new_password1 = None
    new_password2 = None
    new_password = serializers.CharField(write_only=True)

    set_password_form_class = CustomSetPasswordForm

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.adapter: AccountAdapterT = get_adapter()

    def save(self) -> None:
        super().save()
        self.adapter.send_notification_mail("account/email/password_changed", self.user)


class CustomPasswordChangeSerializer(PasswordChangeSerializer):
    new_password1 = None
    new_password2 = None
    new_password = serializers.CharField(write_only=True)

    set_password_form_class = CustomSetPasswordForm

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.adapter: AccountAdapterT = get_adapter()

    def save(self) -> None:
        super().save()
        self.adapter.send_notification_mail("account/email/password_changed", self.user)
