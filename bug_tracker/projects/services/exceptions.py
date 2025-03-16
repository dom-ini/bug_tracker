from datetime import datetime

from core.exceptions import ApplicationException
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class MemberAlreadyInProject(ApplicationException):
    message = _("User already in project.")


class SubdomainRecentlyChanged(ApplicationException):
    @classmethod
    def construct(cls, next_allowed_change: datetime):
        return cls(
            _(
                "Subdomain can only be changed every %(interval)d days. "
                "Next change possible on: %(next_allowed)s"
                % {
                    "interval": settings.SUBDOMAIN_CHANGE_INTERVAL_DAYS,
                    "next_allowed": next_allowed_change.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        )


class NotSufficientRoleInProject(ApplicationException):
    message = _("User does not have required role in the project.")


class UserCannotModifyOwnMembership(ApplicationException):
    message = _("User can't change its own role or remove itself from the project")
