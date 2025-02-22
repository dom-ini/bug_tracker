from typing import Sequence

import pytest
from django.conf import Settings
from django.core import mail as django_mail
from django.core.mail import EmailMessage, send_mail

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def override_email_related_settings(settings: Settings) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CORE_EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.EMAIL_BACKEND = "core.email_backend.AsyncEmailBackend"


@pytest.fixture
def email_messages() -> Sequence[EmailMessage]:
    return [
        EmailMessage(
            subject="test",
            body="test",
            from_email="email@example.com",
            to=["email1@example.com", "email2@example.com"],
        ),
        EmailMessage(
            subject="test2",
            body="test2",
            from_email="email1@example.com",
            to=["email3@example.com"],
        ),
    ]


def test_async_email_backend_sends_messages(email_messages: Sequence[EmailMessage]) -> None:
    mails_sent = 0

    for message in email_messages:
        mails_sent += send_mail(
            subject=message.subject, message=message.body, from_email=message.from_email, recipient_list=message.to
        )

    assert mails_sent == len(email_messages)
    for i, mail in enumerate(django_mail.outbox):
        assert mail.subject == email_messages[i].subject
        assert mail.from_email == email_messages[i].from_email
        assert mail.to == email_messages[i].to
        assert mail.body == email_messages[i].body
