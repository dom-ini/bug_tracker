import pytest
from allauth.account.models import EmailAddress, EmailConfirmation
from django.core import mail
from django.http import HttpRequest
from users.adapters import CustomAccountAdapter
from users.models import CustomUser
from users.url_generators import generate_email_confirmation_url

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_get_email_confirmation_url_returns_expected_url() -> None:
    user = CustomUser.objects.create_user(username="test", email="test@example.com", password="StrongP@ssword1234!")
    email_address = EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)
    email_confirmation = EmailConfirmation.create(email_address)
    email_confirmation.save()

    adapter = CustomAccountAdapter()
    request = HttpRequest()
    url = adapter.get_email_confirmation_url(request, email_confirmation)

    expected_url = generate_email_confirmation_url(email_confirmation.key)
    assert url == expected_url


@pytest.mark.django_db
def test_send_account_already_exists_mail_sends_email() -> None:
    adapter = CustomAccountAdapter()
    email = "existing@example.com"

    assert len(mail.outbox) == 0

    adapter.send_account_already_exists_mail(email)

    assert len(mail.outbox) == 1
    sent_mail = mail.outbox[0]

    assert sent_mail.to == [email]
