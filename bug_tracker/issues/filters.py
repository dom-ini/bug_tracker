from auditlog.models import LogEntry
from core.filters import BaseOrdering
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from issues.models import HistoryEntrySubject, Issue, IssueAttachment, IssueComment


class IssueOrdering(BaseOrdering):
    base_fields = ["title", "status", "priority", "type", "created_at"]


class IssueCommentOrdering(BaseOrdering):
    base_fields = ["created_at"]


class IssueAttachmentOrdering(BaseOrdering):
    base_fields = ["created_at"]


class IssueHistoryOrdering(BaseOrdering):
    base_fields = ["timestamp"]


class IssueFilter(filters.FilterSet):
    order_by = filters.OrderingFilter(fields=IssueOrdering.base_fields)
    unassigned = filters.BooleanFilter(method="filter_unassigned")

    def filter_unassigned(self, queryset: QuerySet[Issue], _name: str, value: bool | None) -> QuerySet[Issue]:
        if value:
            return queryset.filter(assigned_to__isnull=True)
        return queryset

    class Meta:
        model = Issue
        fields = {
            "title": ["icontains"],
            "status": ["exact"],
            "priority": ["exact"],
            "type": ["exact"],
            "assigned_to": ["exact"],
            "created_by": ["exact"],
        }


class IssueCommentFilter(filters.FilterSet):
    order_by = filters.OrderingFilter(fields=IssueCommentOrdering.base_fields)

    class Meta:
        model = IssueComment
        fields = {
            "author": ["exact"],
        }


class IssueAttachmentFilter(filters.FilterSet):
    order_by = filters.OrderingFilter(fields=IssueAttachmentOrdering.base_fields)

    class Meta:
        model = IssueAttachment
        fields = {
            "extension": ["exact"],
        }


class HistoryEntryFilter(filters.FilterSet):
    subject_to_ct = {
        HistoryEntrySubject.ISSUE: ContentType.objects.get_for_model(Issue),
        HistoryEntrySubject.COMMENT: ContentType.objects.get_for_model(IssueComment),
        HistoryEntrySubject.ATTACHMENT: ContentType.objects.get_for_model(IssueAttachment),
    }

    order_by = filters.OrderingFilter(fields=IssueHistoryOrdering.base_fields)
    content_type = filters.ChoiceFilter(choices=subject_to_ct, method="filter_subject")

    def filter_subject(self, queryset: QuerySet[LogEntry], _name: str, value: str | None) -> QuerySet[LogEntry]:
        if value is None:
            return queryset
        ct = self.subject_to_ct.get(value)
        return queryset.filter(content_type=ct)

    class Meta:
        model = LogEntry
        fields = {
            "action": ["exact"],
            "actor": ["exact"],
        }
