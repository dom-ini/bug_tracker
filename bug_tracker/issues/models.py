from auditlog.registry import auditlog
from core.models import BaseModel
from core.validators import validate_file_size, validate_file_type
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


def get_attachment_upload_path(instance: "IssueAttachment", filename: str) -> str:
    issue_path = f"issue-{instance.issue_id}"
    if instance.comment:
        parent_path = f"{issue_path}/comment-{instance.comment_id}"
    else:
        parent_path = issue_path
    return f"{settings.ATTACHMENTS_BASE_PATH}/{parent_path}/{filename}"


class Issue(BaseModel):
    class Status(models.IntegerChoices):
        OPEN = 1, _("open")
        IN_PROGRESS = 2, _("in progress")
        CLOSED = 3, _("closed")

    class Priority(models.IntegerChoices):
        LOW = 1, _("low")
        MEDIUM = 2, _("medium")
        HIGH = 3, _("high")
        CRITICAL = 4, _("critical")

    class Type(models.IntegerChoices):
        BUG = 1, _("bug")
        FEATURE = 2, _("feature")

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=1024, blank=True, null=True)
    status = models.IntegerField(choices=Status, default=Status.OPEN)
    priority = models.IntegerField(choices=Priority, default=Priority.MEDIUM)
    type = models.IntegerField(choices=Type, default=Type.BUG)

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="issues")
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="issues_created")
    assigned_to = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name="issues_assigned"
    )

    class Meta:
        verbose_name = _("Issue")
        verbose_name_plural = _("Issues")

    def __str__(self) -> str:
        return self.title


class IssueComment(BaseModel):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="issue_comments")
    text = models.TextField(max_length=1024)

    class Meta:
        verbose_name = _("Issue comment")
        verbose_name_plural = _("Issue comments")
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.text[:100]


class IssueAttachment(BaseModel):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="attachments")
    comment = models.ForeignKey(
        IssueComment, on_delete=models.CASCADE, related_name="attachments", null=True, blank=True
    )
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="issue_attachments")

    file = models.FileField(upload_to=get_attachment_upload_path, validators=[validate_file_type, validate_file_size])
    extension = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("Issue attachment")
        verbose_name_plural = _("Issue attachments")

    @property
    def url(self) -> str:
        return self.file.url

    def __str__(self) -> str:
        return self.file.name


class HistoryEntrySubject:
    ISSUE = "issue"
    COMMENT = "comment"
    ATTACHMENT = "attachment"

    choices = (
        (ISSUE, Issue._meta.verbose_name),
        (COMMENT, IssueComment._meta.verbose_name),
        (ATTACHMENT, IssueAttachment._meta.verbose_name),
    )


auditlog.register(Issue, include_fields=["title", "description", "status", "priority", "type", "assigned_to"])
auditlog.register(IssueComment, include_fields=["text"])
auditlog.register(IssueAttachment, include_fields=["file", "extension"])
