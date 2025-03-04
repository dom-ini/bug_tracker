from datetime import datetime, timedelta
from typing import TypedDict

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import transaction
from django.utils.timezone import now
from projects.models import Project, ProjectIdentifier, ProjectRole, ProjectRoleAssignment

AllowedSubdomainChangeDate = datetime


class ProjectCreateData(TypedDict):
    name: str
    description: str
    subdomain: str


class ProjectUpdateData(TypedDict):
    name: str | None
    description: str | None
    subdomain: str | None
    status: Project.Status | None


def _create_project(data: ProjectCreateData, user: AbstractBaseUser) -> Project:
    project = Project(
        name=data["name"],
        description=data["description"],
        created_by=user,
    )
    project.validate_and_save()
    return project


def _create_identifier(project: Project, subdomain: str) -> ProjectIdentifier:
    identifier = ProjectIdentifier(project=project, subdomain=subdomain)
    identifier.validate_and_save()
    return identifier


def _create_role_assignment(project: Project, user: AbstractBaseUser, role: str) -> ProjectRoleAssignment:
    assignment = ProjectRoleAssignment(project=project, user=user, role=role)
    assignment.validate_and_save()
    return assignment


def _update_project_data(project: Project, name: str, description: str, status: Project.Status) -> Project:
    project.name = name
    project.description = description
    project.status = status
    project.validate_and_save()
    return project


def _update_subdomain(project: Project, subdomain: str) -> Project:
    project.identifier.subdomain = subdomain
    project.identifier.validate_and_save()
    return project


def is_subdomain_change_allowed(project: Project) -> tuple[bool, AllowedSubdomainChangeDate]:
    cooldown_days = settings.SUBDOMAIN_CHANGE_INTERVAL_DAYS
    last_updated = project.identifier.updated_at
    next_allowed_change = last_updated + timedelta(days=cooldown_days)
    return now() >= next_allowed_change, next_allowed_change


@transaction.atomic
def project_create(*, project_data: ProjectCreateData, user: AbstractBaseUser) -> Project:
    new_project = _create_project(data=project_data, user=user)
    _create_identifier(project=new_project, subdomain=project_data["subdomain"])
    _create_role_assignment(project=new_project, user=user, role=ProjectRole.MANAGER)
    return new_project


@transaction.atomic
def project_update(*, project: Project, project_data: ProjectUpdateData) -> Project:
    name = project_data.get("name", project.name)
    description = project_data.get("description", project.description)
    status = project_data.get("status", project.status)
    subdomain = project_data.get("subdomain", project.subdomain)
    if name or description or status:
        _update_project_data(project=project, name=name, description=description, status=status)
    if subdomain:
        _update_subdomain(project=project, subdomain=subdomain)
    return project
