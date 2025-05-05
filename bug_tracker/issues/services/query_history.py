from typing import Any

from auditlog.models import LogEntry
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet
from issues.filters import HistoryEntryFilter
from issues.services.query_issue import issue_get


def history_list(*, issue_id: int, user: AbstractBaseUser, filters: dict[str, Any] | None = None) -> QuerySet[LogEntry]:
    history = LogEntry.objects.filter(additional_data__issue_id=issue_id)
    issue = issue_get(issue_id=issue_id, user=user)
    queryset = history if issue is not None else LogEntry.objects.none()
    return HistoryEntryFilter(filters, queryset=queryset).qs
