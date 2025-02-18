from typing import Any

from allauth.account import app_settings as allauth_account_settings
from allauth.account.utils import complete_signup
from dj_rest_auth.registration.views import RegisterView, ResendEmailVerificationView
from dj_rest_auth.views import PasswordResetView
from users.models import CustomUser


class EmailThrottleScopeMixin:
    throttle_scope = "email"


class CustomRegisterView(EmailThrottleScopeMixin, RegisterView):
    def dispatch(self, *args: Any, **kwargs: Any) -> Any:
        return super().dispatch(*args, **kwargs)

    def perform_create(self, serializer) -> CustomUser | None:
        user = serializer.save(self.request)
        if user is not None:
            complete_signup(
                self.request._request,
                user,
                allauth_account_settings.EMAIL_VERIFICATION,
                None,
            )
        return user


class CustomPasswordResetView(EmailThrottleScopeMixin, PasswordResetView):
    pass


class CustomResendEmailVerificationView(EmailThrottleScopeMixin, ResendEmailVerificationView):
    pass
