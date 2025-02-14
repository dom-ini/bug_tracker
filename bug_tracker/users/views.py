from typing import Any

from allauth.account import app_settings as allauth_account_settings
from allauth.account.utils import complete_signup
from dj_rest_auth.registration.views import RegisterView
from users.models import CustomUser


class CustomRegisterView(RegisterView):
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
