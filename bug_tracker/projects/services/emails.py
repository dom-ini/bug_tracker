from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from users.url_generators import generate_email_confirmation_url, generate_reset_password_url


def send_invitation_email_for_new_user(
    *, email: str, username: str, user_id: int, password_token: str, email_confirm_token: str, project_name: str
) -> None:
    set_password_url = generate_reset_password_url(user_id=user_id, key=password_token)
    email_confirm_url = generate_email_confirmation_url(email_confirm_token)

    context = {
        "project_name": project_name,
        "set_password_url": set_password_url,
        "email_confirm_url": email_confirm_url,
        "username": username,
        "site_domain": settings.FRONT_DOMAIN,
    }
    message = render_to_string("projects/email/invitation_new_user.txt", context=context)

    send_mail(
        subject=_('You have been invited to the project "%(project_name)s"') % {"project_name": project_name},
        message=message,
        from_email=None,
        recipient_list=[email],
    )


def send_invitation_email_for_existing_user(*, email: str, project_name: str) -> None:
    context = {
        "project_name": project_name,
        "site_domain": settings.FRONT_DOMAIN,
    }
    message = render_to_string("projects/email/invitation_existing_user.txt", context=context)

    send_mail(
        subject=_('You have been invited to the project "%(project_name)s"') % {"project_name": project_name},
        message=message,
        from_email=None,
        recipient_list=[email],
    )
