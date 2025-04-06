import nh3
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import transaction
from issues.models import Issue
from issues.permissions import can_assign_issue, can_create_issue, can_edit_issue, can_remove_issue
from issues.services.emails import send_issue_assignment_notification_email
from issues.services.exceptions import (
    AssigneeDoesNotExistWithinProject,
    IssueActionNotPermitted,
    IssueAlreadyAssignedToGivenAssignee,
)
from projects.models import Project, ProjectRoleAssignment
from projects.services.query_member import member_get


class EmptyAssignment:
    user = None


def _get_empty_assignment() -> EmptyAssignment:
    return EmptyAssignment()


def _get_and_validate_assignee(
    *, assignee_id: int | None, project: Project, requestor: AbstractBaseUser
) -> ProjectRoleAssignment | EmptyAssignment:
    if assignee_id is None:
        return _get_empty_assignment()

    assignee = member_get(project_id=project.id, member_id=assignee_id, user=requestor)
    if assignee is None:
        raise AssigneeDoesNotExistWithinProject
    if not can_assign_issue(project=project, user=requestor, assign_to=assignee.user):
        raise IssueActionNotPermitted(IssueActionNotPermitted.ASSIGN)
    return assignee


def _create_issue(
    *,
    project: Project,
    created_by: AbstractBaseUser,
    assigned_to: AbstractBaseUser | None,
    title: str,
    description: str,
    priority: Issue.Priority,
    issue_type: Issue.Type,
) -> Issue:
    issue = Issue(
        project=project,
        created_by=created_by,
        assigned_to=assigned_to,
        title=title,
        description=description,
        priority=priority,
        type=issue_type,
    )
    issue.validate_and_save()
    return issue


def _update_issue(
    *,
    issue: Issue,
    title: str | None = None,
    description: str | None = None,
    status: Issue.Status | None = None,
    priority: Issue.Priority | None = None,
    issue_type: Issue.Type | None = None,
) -> Issue:
    if title is not None:
        issue.title = title
    if description is not None:
        issue.description = nh3.clean(description)
    if status is not None:
        issue.status = status
    if priority is not None:
        issue.priority = priority
    if issue_type is not None:
        issue.type = issue_type
    issue.validate_and_save()
    return issue


def _assign_to_issue(*, issue: Issue, assignee: AbstractBaseUser | None) -> Issue:
    issue.assigned_to = assignee
    issue.validate_and_save()
    return issue


@transaction.atomic
def issue_create(
    *,
    project: Project,
    created_by: AbstractBaseUser,
    assigned_to_id: int | None,
    title: str,
    description: str,
    priority: Issue.Priority,
    issue_type: Issue.Type,
) -> Issue:
    if not can_create_issue(project=project, user=created_by):
        raise IssueActionNotPermitted(IssueActionNotPermitted.CREATE)

    assigned_to = _get_and_validate_assignee(assignee_id=assigned_to_id, project=project, requestor=created_by).user
    new_issue = _create_issue(
        project=project,
        created_by=created_by,
        assigned_to=assigned_to,
        title=title,
        description=nh3.clean(description),
        priority=priority,
        issue_type=issue_type,
    )
    if assigned_to is not None:
        send_issue_assignment_notification_email(email=assigned_to.email, issue_title=title, issue_id=new_issue.id)
    return new_issue


@transaction.atomic
def issue_remove(*, issue: Issue, editor: AbstractBaseUser) -> None:
    if not can_remove_issue(issue=issue, user=editor):
        raise IssueActionNotPermitted(IssueActionNotPermitted.REMOVE)

    issue.delete()


@transaction.atomic
def issue_update(
    *,
    issue: Issue,
    editor: AbstractBaseUser,
    title: str | None = None,
    description: str | None = None,
    status: Issue.Status | None = None,
    priority: Issue.Priority | None = None,
    issue_type: Issue.Type | None = None,
) -> Issue:
    if not can_edit_issue(issue=issue, user=editor):
        raise IssueActionNotPermitted(IssueActionNotPermitted.EDIT)

    _update_issue(
        issue=issue, title=title, description=description, status=status, priority=priority, issue_type=issue_type
    )
    return issue


@transaction.atomic
def issue_assign(*, issue: Issue, editor: AbstractBaseUser, assigned_to_id: int | None) -> Issue:
    if (issue.assigned_to is None and assigned_to_id is None) or (issue.assigned_to_id == assigned_to_id):
        raise IssueAlreadyAssignedToGivenAssignee

    assigned_to = _get_and_validate_assignee(assignee_id=assigned_to_id, project=issue.project, requestor=editor).user
    _assign_to_issue(issue=issue, assignee=assigned_to)

    if assigned_to is not None:
        send_issue_assignment_notification_email(email=assigned_to.email, issue_title=issue.title, issue_id=issue.id)

    return issue
