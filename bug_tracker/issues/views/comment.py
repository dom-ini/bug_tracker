from core.pagination import LimitOffsetPagination, get_paginated_response
from core.services import query_or_404
from drf_spectacular.utils import extend_schema
from issues.serializers.comment import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    CommentListSerializer,
    CommentUpdateSerializer,
)
from issues.services.command_comment import comment_create, comment_remove, comment_update
from issues.services.exceptions import CommentActionNotPermitted
from issues.services.query_comment import comment_get, comment_list
from issues.services.query_issue import issue_get
from rest_framework import serializers, status, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response


class CommentListCreateView(views.APIView):
    class Pagination(LimitOffsetPagination):
        pass

    class FilterSerializer(serializers.Serializer):
        author = serializers.IntegerField(required=False)

    pagination_class = Pagination

    @extend_schema(
        parameters=[FilterSerializer],
        responses=CommentListSerializer(many=True),
    )
    def get(self, request: Request, issue_id: int) -> Response:
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        comments = comment_list(issue_id=issue_id, user=request.user, filters=filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=CommentListSerializer,
            queryset=comments,
            request=request,
            view=self,
        )

    @extend_schema(request=CommentCreateSerializer, responses={201: CommentDetailSerializer})
    def post(self, request: Request, issue_id: int) -> Response:
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        issue = query_or_404(issue_get, issue_id=issue_id, user=self.request.user)

        new_comment = comment_create(**serializer.validated_data, author=self.request.user, issue=issue)

        data = CommentDetailSerializer(new_comment).data
        return Response(data, status=status.HTTP_201_CREATED)


class CommentDetailUpdateDeleteView(views.APIView):
    @extend_schema(responses=CommentDetailSerializer)
    def get(self, request: Request, issue_id: int, comment_id: int) -> Response:
        comment = query_or_404(comment_get, issue_id=issue_id, comment_id=comment_id, user=self.request.user)

        data = CommentDetailSerializer(comment).data
        return Response(data)

    @extend_schema(responses={204: None})
    def delete(self, request: Request, issue_id: int, comment_id: int) -> Response:
        comment = query_or_404(comment_get, issue_id=issue_id, comment_id=comment_id, user=self.request.user)

        try:
            comment_remove(comment=comment, editor=self.request.user)
        except CommentActionNotPermitted as e:
            raise PermissionDenied(str(e)) from e

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=CommentUpdateSerializer, responses=CommentDetailSerializer)
    def put(self, request: Request, issue_id: int, comment_id: int) -> Response:
        serializer = CommentUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        comment = query_or_404(comment_get, issue_id=issue_id, comment_id=comment_id, user=self.request.user)

        try:
            updated_comment = comment_update(comment=comment, editor=self.request.user, **serializer.validated_data)
        except CommentActionNotPermitted as e:
            raise PermissionDenied(str(e)) from e

        data = CommentDetailSerializer(updated_comment).data
        return Response(data)
