from typing import Any

from auditlog.models import LogEntry
from auditlog.signals import post_log
from django.db.models.signals import post_delete
from django.dispatch import receiver
from issues.models import Issue, IssueAttachment, IssueComment
from issues.services.command_history import history_add_issue_id_to_entry


@receiver(post_delete, sender=IssueAttachment)
def delete_issue_attachment_file(*_args: Any, instance: IssueAttachment, **_kwargs: Any) -> None:
    if instance.file and instance.file.storage.exists(instance.file.name):
        instance.file.delete(save=False)


@receiver(post_log, sender=Issue)
def handle_issue_change_log(*_args: Any, instance: Issue, log_entry: LogEntry | None, **_kwargs: Any) -> None:
    if log_entry is not None:
        history_add_issue_id_to_entry(log_entry=log_entry, issue_id=instance.id)


@receiver(post_log, sender=IssueComment)
def handle_issue_comment_change_log(
    *_args: Any, instance: IssueComment, log_entry: LogEntry | None, **_kwargs: Any
) -> None:
    if log_entry is not None:
        history_add_issue_id_to_entry(log_entry=log_entry, issue_id=instance.issue_id)


@receiver(post_log, sender=IssueAttachment)
def handle_issue_attachment_change_log(
    *_args: Any, instance: IssueAttachment, log_entry: LogEntry | None, **_kwargs: Any
) -> None:
    if log_entry is not None:
        history_add_issue_id_to_entry(log_entry=log_entry, issue_id=instance.issue_id)
