from auditlog.models import LogEntry
from django.db import transaction


@transaction.atomic
def history_add_issue_id_to_entry(*, log_entry: LogEntry, issue_id: int) -> None:
    log_entry.additional_data = {"issue_id": issue_id}
    log_entry.save()
