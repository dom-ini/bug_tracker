from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailConfirmation
from django.http import HttpRequest
from users.url_resolver import generate_email_confirmation_url

from bug_tracker.url_resolver import FrontendUrlType, resolve_front_url


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, _request: HttpRequest, emailconfirmation: EmailConfirmation) -> str:
        return generate_email_confirmation_url(emailconfirmation.key)

    def send_account_already_exists_mail(self, email: str) -> None:
        password_reset_url = resolve_front_url(FrontendUrlType.RESET_PASSWORD)
        ctx = {
            "password_reset_url": password_reset_url,
        }
        self.send_mail("account/email/account_already_exists", email, ctx)
