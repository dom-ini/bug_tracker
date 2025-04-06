import nh3
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import transaction
from issues.models import Issue, IssueComment
from issues.permissions import can_edit_comment, can_remove_comment
from issues.services.exceptions import CommentActionNotPermitted


def _create_comment(*, issue: Issue, author: AbstractBaseUser, text: str) -> IssueComment:
    comment = IssueComment(
        issue=issue,
        author=author,
        text=text,
    )
    comment.validate_and_save()
    return comment


def _update_comment(*, comment: IssueComment, text: str | None = None) -> IssueComment:
    if text is not None:
        comment.text = text
    comment.validate_and_save()
    return comment


@transaction.atomic
def comment_create(*, issue: Issue, author: AbstractBaseUser, text: str) -> IssueComment:
    new_comment = _create_comment(issue=issue, author=author, text=nh3.clean(text))
    return new_comment


@transaction.atomic
def comment_remove(*, comment: IssueComment, editor: AbstractBaseUser) -> None:
    if not can_remove_comment(comment=comment, user=editor):
        raise CommentActionNotPermitted(CommentActionNotPermitted.REMOVE)

    comment.delete()


@transaction.atomic
def comment_update(*, comment: IssueComment, text: str, editor: AbstractBaseUser) -> IssueComment:
    if not can_edit_comment(comment=comment, user=editor):
        raise CommentActionNotPermitted(CommentActionNotPermitted.EDIT)

    _update_comment(comment=comment, text=text)
    return comment
