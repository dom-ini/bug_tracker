import pytest
from django.core import mail
from issues.services.emails import send_issue_assignment_notification_email

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_send_invitation_email_for_existing_user_integration() -> None:
    send_issue_assignment_notification_email(
        email="existinguser@example.com",
        issue_title="Some Issue Title",
        issue_id=1,
    )

    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert "Some Issue Title" in email.subject
    assert "existinguser@example.com" in email.to
    assert "Some Issue Title" in email.body
