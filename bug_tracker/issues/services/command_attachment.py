from typing import Protocol

from core.utils import get_file_extension
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import transaction
from issues.models import Issue, IssueAttachment, IssueComment
from issues.permissions import can_edit_comment, can_edit_issue
from issues.services.exceptions import CommentActionNotPermitted, IssueActionNotPermitted


class File(Protocol):
    name: str


def _create_attachment(
    *, file: File, uploaded_by: AbstractBaseUser, issue: Issue, comment: IssueComment | None
) -> IssueAttachment:
    extension = get_file_extension(file.name)
    attachment = IssueAttachment(
        file=file,
        extension=extension,
        issue=issue,
        comment=comment,
        uploaded_by=uploaded_by,
    )
    attachment.validate_and_save()
    return attachment


@transaction.atomic
def attachment_add_to_issue(*, uploaded_by: AbstractBaseUser, issue: Issue, file: File) -> IssueAttachment:
    if not can_edit_issue(issue=issue, user=uploaded_by):
        raise IssueActionNotPermitted(IssueActionNotPermitted.EDIT)

    new_attachment = _create_attachment(file=file, issue=issue, comment=None, uploaded_by=uploaded_by)
    return new_attachment


@transaction.atomic
def attachment_add_to_comment(*, uploaded_by: AbstractBaseUser, comment: IssueComment, file) -> IssueAttachment:
    if not can_edit_comment(comment=comment, user=uploaded_by):
        raise CommentActionNotPermitted(CommentActionNotPermitted.EDIT)

    new_attachment = _create_attachment(file=file, issue=comment.issue, comment=comment, uploaded_by=uploaded_by)
    return new_attachment


@transaction.atomic
def attachment_remove(*, attachment: IssueAttachment, requestor: AbstractBaseUser) -> None:
    if attachment.comment is not None and not can_edit_comment(comment=attachment.comment, user=requestor):
        raise CommentActionNotPermitted(CommentActionNotPermitted.EDIT)
    elif attachment.comment is None and not can_edit_issue(issue=attachment.issue, user=requestor):
        raise IssueActionNotPermitted(IssueActionNotPermitted.EDIT)

    attachment.delete()
