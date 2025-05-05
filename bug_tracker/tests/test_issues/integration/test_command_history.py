import pytest
from auditlog.models import LogEntry
from issues.models import Issue
from issues.services import command_history

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_history_add_issue_id_to_entry(issue_1: Issue) -> None:
    entry = LogEntry.objects.log_create(instance=issue_1, force_log=True, action=LogEntry.Action.ACCESS)

    command_history.history_add_issue_id_to_entry(log_entry=entry, issue_id=issue_1.id)

    assert entry.additional_data["issue_id"] == issue_1.id
