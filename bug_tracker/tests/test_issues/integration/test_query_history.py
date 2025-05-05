import pytest
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from issues.models import Issue, IssueComment
from issues.services import query_history
from projects.models import Project
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_history_list_returns_issue_history(
    issue_1: Issue, comment_1: IssueComment, comment_2: IssueComment, user_1: CustomUser, project_1: Project
) -> None:
    issue_ct = ContentType.objects.get_for_model(Issue)
    comment_ct = ContentType.objects.get_for_model(IssueComment)

    history = query_history.history_list(issue_id=issue_1.id, user=user_1)

    entries = {(h.action, h.content_type_id) for h in history}
    assert history.count() == 3
    assert entries == {
        (LogEntry.Action.CREATE, issue_ct.id),
        (LogEntry.Action.CREATE, comment_ct.id),
        (LogEntry.Action.CREATE, comment_ct.id),
    }


@pytest.mark.django_db
def test_history_list_returns_empty_if_requestor_not_part_of_project(
    issue_1: Issue, comment_1: IssueComment, comment_2: IssueComment, user_2: CustomUser
) -> None:
    history = query_history.history_list(issue_id=issue_1.id, user=user_2)

    assert history.count() == 0


@pytest.mark.django_db
def test_history_list_returns_empty_if_invalid_issue_id(user_1: CustomUser) -> None:
    issues = query_history.history_list(issue_id=999, user=user_1)

    assert issues.count() == 0
