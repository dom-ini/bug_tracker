from django.contrib.auth.base_user import AbstractBaseUser
from issues.models import Issue, IssueComment
from projects.models import Project, ProjectRole
from projects.services.query_project import project_get_user_role, project_has_user_roles

CREATE_ISSUE_ALLOWED_ROLES = [ProjectRole.MANAGER, ProjectRole.DEVELOPER, ProjectRole.REPORTER]


def can_create_issue(*, project: Project, user: AbstractBaseUser) -> bool:
    return project_has_user_roles(project=project, user=user, roles=CREATE_ISSUE_ALLOWED_ROLES)


def can_assign_issue(*, project: Project, user: AbstractBaseUser, assign_to: AbstractBaseUser) -> bool:
    user_role = project_get_user_role(project=project, user=user)

    if user_role == ProjectRole.REPORTER:
        return False
    elif user_role == ProjectRole.DEVELOPER:
        return user == assign_to
    elif user_role == ProjectRole.MANAGER:
        return True
    return False


def can_remove_issue(*, issue: Issue, user: AbstractBaseUser) -> bool:
    user_role = project_get_user_role(project=issue.project, user=user)

    if user_role == ProjectRole.REPORTER:
        return False
    elif user_role == ProjectRole.DEVELOPER:
        return issue.created_by == user
    elif user_role == ProjectRole.MANAGER:
        return True
    return False


def can_edit_issue(*, issue: Issue, user: AbstractBaseUser) -> bool:
    user_role = project_get_user_role(project=issue.project, user=user)

    if user_role in [ProjectRole.REPORTER, ProjectRole.DEVELOPER]:
        return issue.created_by == user
    elif user_role == ProjectRole.MANAGER:
        return True
    return False


def can_remove_comment(*, comment: IssueComment, user: AbstractBaseUser) -> bool:
    return comment.author == user


def can_edit_comment(*, comment: IssueComment, user: AbstractBaseUser) -> bool:
    return comment.author == user
