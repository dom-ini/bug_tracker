import pytest
from issues.models import Issue
from issues.services import query_issue
from projects.models import Project
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_issue_get_returns_correct_issue(issue_1: Issue, user_1: CustomUser) -> None:
    issue = query_issue.issue_get(issue_id=issue_1.id, user=user_1)

    assert issue.id == issue_1.id
    assert issue.title == issue_1.title


@pytest.mark.django_db
def test_issue_get_returns_none_if_requestor_not_part_of_project(issue_1: Issue, user_2: CustomUser) -> None:
    issue = query_issue.issue_get(issue_id=issue_1.id, user=user_2)

    assert issue is None


@pytest.mark.django_db
def test_issue_get_returns_none_if_invalid_issue_id(user_1: CustomUser) -> None:
    issue = query_issue.issue_get(issue_id=999, user=user_1)

    assert issue is None


@pytest.mark.django_db
def test_issue_list_returns_project_issues(
    issue_1: Issue, issue_2: Issue, user_1: CustomUser, project_1: Project
) -> None:
    issues = query_issue.issue_list(project_id=project_1.id, user=user_1)

    issue_ids = {i.id for i in issues}
    assert issues.count() == 2
    assert issue_1.id in issue_ids
    assert issue_2.id in issue_ids


@pytest.mark.django_db
def test_issue_list_returns_empty_if_requestor_not_part_of_project(
    project_1: Project, issue_1: Issue, issue_2: Issue, user_2: CustomUser
) -> None:
    issues = query_issue.issue_list(project_id=project_1.id, user=user_2)

    assert issues.count() == 0


@pytest.mark.django_db
def test_issue_list_returns_empty_if_invalid_project_id(project_1: Project, user_1: CustomUser) -> None:
    issues = query_issue.issue_list(project_id=999, user=user_1)

    assert issues.count() == 0
