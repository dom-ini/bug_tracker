from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet
from issues.filters import IssueAttachmentFilter
from issues.models import IssueAttachment


def attachment_list_for_issue(
    *, issue_id: int, user: AbstractBaseUser, filters: dict[str, Any] | None = None
) -> QuerySet[IssueAttachment]:
    attachments = IssueAttachment.objects.filter(issue_id=issue_id, issue__project__members=user)
    return IssueAttachmentFilter(filters, queryset=attachments).qs


def attachment_list_for_comment(
    *, issue_id: int, comment_id: int, user: AbstractBaseUser, filters: dict[str, Any] | None = None
) -> QuerySet[IssueAttachment]:
    attachments = IssueAttachment.objects.filter(comment_id=comment_id, issue_id=issue_id, issue__project__members=user)
    return IssueAttachmentFilter(filters, queryset=attachments).qs


def attachment_get(*, attachment_id: int, issue_id: int, user: AbstractBaseUser) -> IssueAttachment | None:
    attachment = IssueAttachment.objects.filter(
        id=attachment_id, issue_id=issue_id, issue__project__members=user
    ).first()
    return attachment
