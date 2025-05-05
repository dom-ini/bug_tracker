from auditlog.models import LogEntry
from core.pagination import LimitOffsetPagination, get_paginated_response
from core.serializers import CommaSeparatedMultipleChoiceField
from drf_spectacular.utils import extend_schema
from issues.filters import IssueHistoryOrdering
from issues.models import HistoryEntrySubject
from issues.serializers.history import HistoryEntryListSerializer
from issues.services.query_history import history_list
from rest_framework import serializers, views
from rest_framework.request import Request
from rest_framework.response import Response


class HistoryListView(views.APIView):
    class Pagination(LimitOffsetPagination):
        pass

    class FilterSerializer(serializers.Serializer):
        action = serializers.ChoiceField(choices=LogEntry.Action.choices, required=False)
        actor = serializers.IntegerField(required=False)
        content_type = serializers.ChoiceField(choices=HistoryEntrySubject.choices, required=False)
        order_by = CommaSeparatedMultipleChoiceField(choices=IssueHistoryOrdering.fields, required=False)

    pagination_class = Pagination

    @extend_schema(
        parameters=[FilterSerializer],
        responses=HistoryEntryListSerializer(many=True),
    )
    def get(self, request: Request, issue_id: int) -> Response:
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        history = history_list(issue_id=issue_id, user=request.user, filters=filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=HistoryEntryListSerializer,
            queryset=history,
            request=request,
            view=self,
        )
