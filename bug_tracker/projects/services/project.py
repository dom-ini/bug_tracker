from datetime import datetime, timedelta

import nh3
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import transaction
from django.utils.timezone import now
from projects.models import Project, ProjectIdentifier, ProjectRole, ProjectRoleAssignment
from projects.permissions import can_edit_project
from projects.services.exceptions import NotSufficientRoleInProject, SubdomainRecentlyChanged

AllowedSubdomainChangeDate = datetime


def _create_project(*, name: str, description: str, user: AbstractBaseUser) -> Project:
    project = Project(
        name=name,
        description=nh3.clean(description),
        created_by=user,
    )
    project.validate_and_save()
    return project


def _create_identifier(*, project: Project, subdomain: str) -> ProjectIdentifier:
    identifier = ProjectIdentifier(project=project, subdomain=subdomain)
    identifier.validate_and_save()
    return identifier


def _create_role_assignment(*, project: Project, user: AbstractBaseUser, role: str) -> ProjectRoleAssignment:
    assignment = ProjectRoleAssignment(project=project, user=user, role=role)
    assignment.validate_and_save()
    return assignment


def _update_project_data(
    *, project: Project, name: str | None = None, description: str | None = None, status: Project.Status | None = None
) -> Project:
    if name:
        project.name = name
    if description:
        project.description = nh3.clean(description)
    if status:
        project.status = status
    project.validate_and_save()
    return project


def _update_subdomain(*, project: Project, subdomain: str) -> Project:
    project.identifier.subdomain = subdomain
    project.identifier.validate_and_save()
    return project


def is_subdomain_change_allowed(project: Project) -> tuple[bool, AllowedSubdomainChangeDate]:
    cooldown_days = settings.SUBDOMAIN_CHANGE_INTERVAL_DAYS
    last_updated = project.identifier.updated_at
    next_allowed_change = last_updated + timedelta(days=cooldown_days)
    return now() >= next_allowed_change, next_allowed_change


@transaction.atomic
def project_create(*, name: str, description: str, subdomain: str, user: AbstractBaseUser) -> Project:
    new_project = _create_project(name=name, description=description, user=user)
    _create_identifier(project=new_project, subdomain=subdomain)
    _create_role_assignment(project=new_project, user=user, role=ProjectRole.MANAGER)
    return new_project


@transaction.atomic
def project_update(
    *,
    project: Project,
    editor: AbstractBaseUser,
    name: str | None = None,
    description: str | None = None,
    subdomain: str | None = None,
    status: Project.Status | None = None,
) -> Project:
    if not can_edit_project(project=project, user=editor):
        raise NotSufficientRoleInProject()

    is_change_allowed, next_allowed_change = is_subdomain_change_allowed(project)
    if subdomain and not is_change_allowed:
        raise SubdomainRecentlyChanged.construct(next_allowed_change)

    if name or description or status:
        _update_project_data(project=project, name=name, description=description, status=status)
    if subdomain:
        _update_subdomain(project=project, subdomain=subdomain)
    return project
