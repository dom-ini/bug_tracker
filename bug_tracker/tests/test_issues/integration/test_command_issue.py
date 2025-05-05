import pytest
from django.core import mail
from django.core.exceptions import ValidationError
from issues.models import Issue
from issues.services import command_issue, query_issue
from issues.services.exceptions import (
    AssigneeDoesNotExistWithinProject,
    IssueActionNotPermitted,
    IssueAlreadyAssignedToGivenAssignee,
)
from projects.models import Project, ProjectRole
from projects.services import command_member
from tests.factories import fake_issue, fake_user
from tests.utils import clear_outbox
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.fixture
def user_reporter(user_1: CustomUser, project_1: Project) -> CustomUser:
    user = fake_user()
    command_member.member_add_to_project(project=project_1, editor=user_1, email=user.email, role=ProjectRole.REPORTER)
    return user


@pytest.fixture
def user_not_member() -> CustomUser:
    return fake_user()


@pytest.mark.django_db
def test_issue_create(user_1: CustomUser, project_1: Project) -> None:
    issue = command_issue.issue_create(
        project=project_1,
        created_by=user_1,
        assigned_to_id=None,
        title="issue title",
        description="issue description",
        priority=Issue.Priority.MEDIUM,
        issue_type=Issue.Type.FEATURE,
    )

    assert issue.project == project_1
    assert issue.created_by == user_1
    assert issue.title == "issue title"
    assert issue.description == "issue description"
    assert issue.priority == Issue.Priority.MEDIUM
    assert issue.type == Issue.Type.FEATURE


@pytest.mark.django_db
def test_issue_create_does_not_send_mail_if_no_assignment(
    user_1: CustomUser, project_1: Project, issue_1: Issue
) -> None:
    assert issue_1.assigned_to_id is None
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_issue_create_sends_mail_if_assigned(user_1: CustomUser, project_1: Project) -> None:
    issue = fake_issue(project=project_1, user=user_1, assigned_to_id=user_1.id)

    assert issue.assigned_to == user_1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == user_1.email


@pytest.mark.django_db
def test_issue_create_with_invalid_data(user_1: CustomUser, project_1: Project) -> None:
    with pytest.raises(ValidationError):
        command_issue.issue_create(
            project=project_1,
            created_by=user_1,
            assigned_to_id=None,
            title="title",
            description="description",
            priority=999,
            issue_type=999,
        )


@pytest.mark.django_db
def test_issue_create_assignee_not_member_of_project_should_fail(user_1: CustomUser, project_1: Project) -> None:
    with pytest.raises(AssigneeDoesNotExistWithinProject):
        command_issue.issue_create(
            project=project_1,
            created_by=user_1,
            assigned_to_id=999,
            title="title",
            description="description",
            priority=Issue.Priority.MEDIUM,
            issue_type=Issue.Type.FEATURE,
        )


@pytest.mark.django_db
def test_issue_create_with_not_enough_permission_to_create(user_2: CustomUser, project_1: Project) -> None:
    with pytest.raises(IssueActionNotPermitted):
        command_issue.issue_create(
            project=project_1,
            created_by=user_2,
            assigned_to_id=None,
            title="title",
            description="description",
            priority=Issue.Priority.MEDIUM,
            issue_type=Issue.Type.FEATURE,
        )


@pytest.mark.django_db
def test_issue_create_with_not_enough_permission_to_assign(
    user_1: CustomUser, user_reporter: CustomUser, project_1: Project
) -> None:
    with pytest.raises(IssueActionNotPermitted):
        command_issue.issue_create(
            project=project_1,
            created_by=user_reporter,
            assigned_to_id=user_1.id,
            title="title",
            description="description",
            priority=Issue.Priority.MEDIUM,
            issue_type=Issue.Type.FEATURE,
        )


@pytest.mark.django_db
def test_issue_create_description_should_be_cleaned(project_1: Project, user_1: CustomUser) -> None:
    malicious_description = "<script>alert('Malicious')</script>safe part of description<p>should not be stripped</p>"

    issue = command_issue.issue_create(
        project=project_1,
        created_by=user_1,
        assigned_to_id=None,
        title="title",
        description=malicious_description,
        priority=Issue.Priority.MEDIUM,
        issue_type=Issue.Type.FEATURE,
    )

    assert issue.description == "safe part of description<p>should not be stripped</p>"


@pytest.mark.django_db
def test_issue_remove(issue_1: Issue, user_1: CustomUser) -> None:
    issue_id = issue_1.id

    command_issue.issue_remove(issue=issue_1, editor=user_1)

    issue = query_issue.issue_get(issue_id=issue_id, user=user_1)
    assert issue is None


@pytest.mark.django_db
def test_issue_remove_with_not_enough_permission(issue_1: Issue, user_2: CustomUser) -> None:
    with pytest.raises(IssueActionNotPermitted):
        command_issue.issue_remove(issue=issue_1, editor=user_2)


@pytest.mark.django_db
def test_issue_update(issue_1: Issue, user_1: CustomUser) -> None:
    old_title = issue_1.title
    old_type = issue_1.type

    updated_issue = command_issue.issue_update(
        issue=issue_1,
        editor=user_1,
        description="new description",
        status=Issue.Status.CLOSED,
        priority=Issue.Priority.CRITICAL,
    )

    assert updated_issue.title == old_title
    assert updated_issue.type == old_type
    assert updated_issue.description == "new description"
    assert updated_issue.status == Issue.Status.CLOSED
    assert updated_issue.priority == Issue.Priority.CRITICAL


@pytest.mark.django_db
def test_issue_update_description_should_be_cleaned(issue_1: Issue, user_1: CustomUser) -> None:
    malicious_description = "<script>alert('Malicious')</script>safe part of description<p>should not be stripped</p>"

    updated_issue = command_issue.issue_update(issue=issue_1, editor=user_1, description=malicious_description)

    assert updated_issue.description == "safe part of description<p>should not be stripped</p>"


@pytest.mark.django_db
def test_issue_update_with_invalid_data(issue_1: Issue, user_1: CustomUser) -> None:
    with pytest.raises(ValidationError):
        command_issue.issue_update(issue=issue_1, editor=user_1, issue_type=999)


@pytest.mark.django_db
def test_issue_update_with_not_enough_permission(issue_1: Issue, user_2: CustomUser) -> None:
    with pytest.raises(IssueActionNotPermitted):
        command_issue.issue_update(issue=issue_1, editor=user_2, title="new title")


@pytest.mark.django_db
def test_issue_assign_to_none(issue_1: Issue, user_1: CustomUser) -> None:
    command_issue.issue_assign(issue=issue_1, editor=user_1, assigned_to_id=user_1.id)
    clear_outbox()

    updated_issue = command_issue.issue_assign(issue=issue_1, editor=user_1, assigned_to_id=None)

    assert updated_issue.assigned_to is None
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_issue_assign_to_someone(issue_1: Issue, user_1: CustomUser, user_reporter: CustomUser) -> None:
    clear_outbox()

    updated_issue = command_issue.issue_assign(issue=issue_1, editor=user_1, assigned_to_id=user_reporter.id)

    assert updated_issue.assigned_to == user_reporter
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == user_reporter.email


@pytest.mark.django_db
def test_issue_assign_to_already_assigned_should_fail(issue_1: Issue, user_1: CustomUser) -> None:
    command_issue.issue_assign(issue=issue_1, editor=user_1, assigned_to_id=user_1.id)

    with pytest.raises(IssueAlreadyAssignedToGivenAssignee):
        command_issue.issue_assign(issue=issue_1, editor=user_1, assigned_to_id=user_1.id)


@pytest.mark.django_db
def test_issue_assign_to_already_assigned_none_should_fail(issue_1: Issue, user_1: CustomUser) -> None:
    with pytest.raises(IssueAlreadyAssignedToGivenAssignee):
        command_issue.issue_assign(issue=issue_1, editor=user_1, assigned_to_id=None)


@pytest.mark.django_db
def test_issue_assign_assignee_not_member_of_project_should_fail(
    issue_1: Issue, user_1: CustomUser, user_not_member: CustomUser
) -> None:
    with pytest.raises(AssigneeDoesNotExistWithinProject):
        command_issue.issue_assign(issue=issue_1, editor=user_1, assigned_to_id=user_not_member.id)


@pytest.mark.django_db
def test_issue_assign_with_not_enough_permission(issue_1: Issue, user_reporter: CustomUser) -> None:
    with pytest.raises(IssueActionNotPermitted):
        command_issue.issue_assign(issue=issue_1, editor=user_reporter, assigned_to_id=user_reporter.id)
