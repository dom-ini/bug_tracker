from django.contrib.auth.base_user import AbstractBaseUser
from projects.models import Project, ProjectRole
from projects.services.query_project import project_has_user_roles


def can_edit_project(*, project: Project, user: AbstractBaseUser) -> bool:
    return project_has_user_roles(project=project, user=user, roles=[ProjectRole.MANAGER])


def can_edit_members(*, project: Project, user: AbstractBaseUser) -> bool:
    return project_has_user_roles(project=project, user=user, roles=[ProjectRole.MANAGER])
