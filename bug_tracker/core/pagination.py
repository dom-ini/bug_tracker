from typing import Sequence

from django.db.models import QuerySet
from django.views import View
from rest_framework.pagination import BasePagination, LimitOffsetPagination as _LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer


def get_paginated_response(
    *,
    pagination_class: type[BasePagination],
    serializer_class: type[Serializer],
    queryset: QuerySet,
    request: Request,
    view: View,
):
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return Response(serializer.data)


class LimitOffsetPagination(_LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

    def get_paginated_response(self, data: Sequence) -> Response:
        return Response(
            {
                "limit": self.limit,
                "offset": self.offset,
                "count": self.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
