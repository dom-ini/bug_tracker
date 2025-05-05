from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from issues.models import Issue, IssueAttachment, IssueComment


class IssueAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "priority", "type", "assigned_to", "created_by", "project", "created_at"]
    list_filter = ["status", "priority", "type"]
    search_fields = ["title"]
    date_hierarchy = "created_at"


class IssueCommentAdmin(admin.ModelAdmin):
    content_max_len = 30
    list_display = ["content", "issue", "author", "created_at"]
    search_fields = ["text"]
    date_hierarchy = "created_at"

    @admin.display(description=_("Content"), ordering="text")
    def content(self, obj: IssueComment) -> str:
        if len(obj.text) <= self.content_max_len:
            return obj.text
        return obj.text[: self.content_max_len] + "..."


class IssueAttachmentAdmin(admin.ModelAdmin):
    list_display = ["instance", "file", "extension", "issue", "comment", "uploaded_by", "created_at"]
    list_filter = ["extension"]
    date_hierarchy = "created_at"
    readonly_fields = ["extension", "file"]

    @admin.display(description=_("Attachment"))
    def instance(self, obj: IssueAttachment) -> str:
        url = reverse("admin:issues_issueattachment_change", kwargs={"object_id": obj.id})
        return format_html("<a href='{0}'>{1}</a>", url, _("details"))


admin.site.register(Issue, IssueAdmin)
admin.site.register(IssueComment, IssueCommentAdmin)
admin.site.register(IssueAttachment, IssueAttachmentAdmin)
