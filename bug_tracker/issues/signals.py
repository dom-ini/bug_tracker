from typing import Any

from django.db.models.signals import post_delete
from django.dispatch import receiver
from issues.models import IssueAttachment


@receiver(post_delete, sender=IssueAttachment)
def delete_issue_attachment_file(*_args: Any, instance: IssueAttachment, **_kwargs: Any) -> None:
    if instance.file and instance.file.storage.exists(instance.file.name):
        instance.file.delete(save=False)
