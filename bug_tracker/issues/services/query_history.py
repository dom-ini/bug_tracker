from typing import Any

from auditlog.models import LogEntry
from django.db.models import QuerySet
from issues.filters import HistoryEntryFilter
from issues.models import Issue


def history_list(*, issue: Issue, filters: dict[str, Any]) -> QuerySet[LogEntry]:
    history = LogEntry.objects.filter(additional_data__issue_id=issue.id)
    return HistoryEntryFilter(filters, queryset=history).qs
