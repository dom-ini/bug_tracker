from typing import Any, Sequence

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import OuterRef, QuerySet, Subquery
from projects.filters import ProjectFilter
from projects.models import Project, ProjectRole, ProjectRoleAssignment


def _get_role_subquery(user: AbstractBaseUser) -> QuerySet[ProjectRoleAssignment, dict[str, Any]]:
    return ProjectRoleAssignment.objects.filter(project=OuterRef("id"), user=user).values("role")[:1]


def project_get(*, project_id: int, user: AbstractBaseUser) -> Project | None:
    role_subquery = _get_role_subquery(user=user)
    project = Project.objects.filter(id=project_id, members=user).annotate(role=Subquery(role_subquery)).first()
    return project


def project_get_by_subdomain(*, subdomain: str, user: AbstractBaseUser) -> Project | None:
    role_subquery = _get_role_subquery(user=user)
    project = (
        Project.objects.filter(identifier__subdomain=subdomain, members=user)
        .annotate(role=Subquery(role_subquery))
        .first()
    )
    return project


def project_list(*, user: AbstractBaseUser, filters: dict[str, Any] | None = None) -> QuerySet[Project]:
    role_subquery = _get_role_subquery(user=user)
    queryset = Project.objects.filter(members=user).annotate(role=Subquery(role_subquery))
    return ProjectFilter(filters, queryset=queryset).qs


def project_get_user_role(*, project: Project, user: AbstractBaseUser) -> str | None:
    assignment = ProjectRoleAssignment.objects.filter(project=project, user=user).first()
    if not assignment:
        return None
    return assignment.role


def project_has_user_roles(*, project: Project, user: AbstractBaseUser, roles: Sequence[ProjectRole]) -> bool:
    user_role = project_get_user_role(project=project, user=user)
    if not user_role:
        return False
    return user_role in roles
