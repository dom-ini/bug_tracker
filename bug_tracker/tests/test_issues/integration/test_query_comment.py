import pytest
from issues.models import Issue, IssueComment
from issues.services import query_comment
from projects.models import Project
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_comment_get_returns_correct_comment(issue_1: Issue, comment_1: IssueComment, user_1: CustomUser) -> None:
    comment = query_comment.comment_get(comment_id=comment_1.id, issue_id=issue_1.id, user=user_1)

    assert comment.id == comment_1.id
    assert comment.issue == issue_1
    assert comment.author == user_1


@pytest.mark.django_db
def test_comment_get_returns_none_if_requestor_not_part_of_project(
    issue_1: Issue, comment_1: IssueComment, user_2: CustomUser
) -> None:
    comment = query_comment.comment_get(comment_id=comment_1.id, issue_id=issue_1.id, user=user_2)

    assert comment is None


@pytest.mark.django_db
def test_comment_get_returns_none_if_invalid_issue_id(comment_1: IssueComment, user_1: CustomUser) -> None:
    comment = query_comment.comment_get(comment_id=comment_1.id, issue_id=999, user=user_1)

    assert comment is None


@pytest.mark.django_db
def test_comment_get_returns_none_if_invalid_comment_id(issue_1: Issue, user_1: CustomUser) -> None:
    comment = query_comment.comment_get(comment_id=999, issue_id=issue_1.id, user=user_1)

    assert comment is None


@pytest.mark.django_db
def test_comment_list_returns_issue_comments(
    issue_1: Issue, comment_1: IssueComment, comment_2: IssueComment, user_1: CustomUser, project_1: Project
) -> None:
    comments = query_comment.comment_list(issue_id=issue_1.id, user=user_1)

    comment_ids = {c.id for c in comments}
    assert comments.count() == 2
    assert comment_1.id in comment_ids
    assert comment_2.id in comment_ids


@pytest.mark.django_db
def test_comment_list_returns_empty_if_requestor_not_part_of_project(
    issue_1: Issue, comment_1: IssueComment, comment_2: IssueComment, user_2: CustomUser
) -> None:
    comments = query_comment.comment_list(issue_id=issue_1.id, user=user_2)

    assert comments.count() == 0


@pytest.mark.django_db
def test_comment_list_returns_empty_if_invalid_issue_id(user_1: CustomUser) -> None:
    issues = query_comment.comment_list(issue_id=999, user=user_1)

    assert issues.count() == 0
