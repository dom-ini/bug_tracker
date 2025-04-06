from django.contrib import admin
from issues.models import Issue, IssueAttachment, IssueComment

admin.site.register((Issue, IssueComment, IssueAttachment))
