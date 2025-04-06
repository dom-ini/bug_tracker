from core.filters import BaseOrdering
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from issues.models import Issue, IssueComment


class IssueOrdering(BaseOrdering):
    base_fields = ["title", "status", "priority", "type", "created_at"]


class IssueCommentOrdering(BaseOrdering):
    base_fields = ["created_at"]


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
