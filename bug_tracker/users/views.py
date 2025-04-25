from allauth.account import app_settings as allauth_account_settings
from allauth.account.utils import complete_signup
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.registration.views import RegisterView, ResendEmailVerificationView
from dj_rest_auth.views import PasswordResetView
from django.contrib.auth.base_user import AbstractBaseUser


class EmailThrottleScopeMixin:
    throttle_scope = "email"


class CustomRegisterView(EmailThrottleScopeMixin, RegisterView):
    def perform_create(self, serializer: RegisterSerializer) -> AbstractBaseUser | None:
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
