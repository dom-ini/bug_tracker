import pytest
from issues.models import Issue, IssueComment
from issues.services import command_comment, query_comment
from issues.services.exceptions import CommentActionNotPermitted
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_comment_create(issue_1: Issue, user_1: CustomUser) -> None:
    comment = command_comment.comment_create(issue=issue_1, author=user_1, text="new comment")

    assert comment.author == user_1
    assert comment.text == "new comment"
    assert comment.issue == issue_1


@pytest.mark.django_db
def test_comment_update(comment_1: IssueComment, user_1: CustomUser) -> None:
    updated_comment = command_comment.comment_update(comment=comment_1, editor=user_1, text="updated comment")

    assert updated_comment.text == "updated comment"


@pytest.mark.django_db
def test_comment_update_with_not_enough_permission(comment_1: IssueComment, user_2: CustomUser) -> None:
    with pytest.raises(CommentActionNotPermitted):
        command_comment.comment_update(comment=comment_1, editor=user_2, text="updated comment")


@pytest.mark.django_db
def test_comment_remove(comment_1: IssueComment, issue_1: Issue, user_1: CustomUser) -> None:
    comment_id = comment_1.id

    command_comment.comment_remove(comment=comment_1, editor=user_1)

    comment = query_comment.comment_get(comment_id=comment_id, issue_id=issue_1.id, user=user_1)
    assert comment is None


@pytest.mark.django_db
def test_comment_remove_with_not_enough_permission(comment_1: IssueComment, user_2: CustomUser) -> None:
    with pytest.raises(CommentActionNotPermitted):
        command_comment.comment_remove(comment=comment_1, editor=user_2)
