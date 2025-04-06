from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet
from issues.filters import IssueCommentFilter
from issues.models import IssueComment


def comment_list(
    *, issue_id: int, user: AbstractBaseUser, filters: dict[str, Any] | None = None
) -> QuerySet[IssueComment]:
    comments = IssueComment.objects.filter(issue_id=issue_id, issue__project__members=user)
    return IssueCommentFilter(filters, queryset=comments).qs


def comment_get(*, comment_id: int, issue_id: int, user: AbstractBaseUser) -> IssueComment | None:
    comment = IssueComment.objects.filter(id=comment_id, issue_id=issue_id, issue__project__members=user).first()
    return comment
