from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet
from issues.filters import IssueFilter
from issues.models import Issue


def issue_list(*, project_id: int, user: AbstractBaseUser, filters: dict[str, Any] | None = None) -> QuerySet[Issue]:
    issues = Issue.objects.filter(project_id=project_id, project__members=user)
    return IssueFilter(filters, queryset=issues).qs


def issue_get(*, issue_id: int, user: AbstractBaseUser) -> Issue | None:
    issue = Issue.objects.filter(id=issue_id, project__members=user).first()
    return issue
