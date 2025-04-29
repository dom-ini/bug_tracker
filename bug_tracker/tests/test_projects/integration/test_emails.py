import pytest
from django.core import mail
from projects.services.emails import send_invitation_email_for_existing_user, send_invitation_email_for_new_user

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_send_invitation_email_for_new_user_integration() -> None:
    send_invitation_email_for_new_user(
        email="newuser@example.com",
        username="newuser",
        user_id=1,
        password_token="reset-token",
        email_confirm_token="confirm-token",
        project_name="New Project Name",
        project_id=1,
    )

    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert "New Project Name" in email.subject
    assert "newuser@example.com" in email.to
    assert "New Project Name" in email.body
    assert "newuser" in email.body
    assert "reset-token" in email.body
    assert "confirm-token" in email.body


@pytest.mark.django_db
def test_send_invitation_email_for_existing_user_integration() -> None:
    send_invitation_email_for_existing_user(
        email="existinguser@example.com",
        project_name="Existing Project Name",
        project_id=2,
    )

    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert "Existing Project Name" in email.subject
    assert "existinguser@example.com" in email.to
    assert "Existing Project" in email.body
