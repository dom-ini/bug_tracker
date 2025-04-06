from core.url_resolver import FrontendUrlType, resolve_front_url
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def send_issue_assignment_notification_email(*, email: str, issue_title: str, issue_id: int) -> None:
    issue_url = f"{resolve_front_url(FrontendUrlType.ISSUES)}/{issue_id}"
    context = {
        "issue_title": issue_title,
        "site_domain": settings.FRONT_DOMAIN,
        "issue_url": issue_url,
    }
    message = render_to_string("issues/email/assignment_notification.txt", context=context)

    send_mail(
        subject=_('You have been assigned a new issue "%(issue_title)s"') % {"issue_title": issue_title},
        message=message,
        from_email=None,
        recipient_list=[email],
    )
