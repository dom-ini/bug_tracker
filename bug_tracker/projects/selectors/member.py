from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import F, QuerySet
from projects.filters import MemberFilter
from projects.models import ProjectRoleAssignment


def _get_user_fields_annotation() -> dict[str, F]:
    return {"first_name": F("user__first_name"), "last_name": F("user__last_name"), "email": F("user__email")}


def member_get(*, project_id: int, member_id: int, user: AbstractBaseUser) -> ProjectRoleAssignment | None:
    assignment = (
        ProjectRoleAssignment.objects.filter(project_id=project_id, project__members=user, user__id=member_id)
        .annotate(**_get_user_fields_annotation())
        .first()
    )
    return assignment


def member_list(
    *, project_id: int, user: AbstractBaseUser, filters: dict[str, Any] | None = None
) -> QuerySet[ProjectRoleAssignment]:
    assignments = ProjectRoleAssignment.objects.filter(project_id=project_id, project__members=user).annotate(
        **_get_user_fields_annotation()
    )
    return MemberFilter(filters, queryset=assignments).qs
