from abc import ABC, abstractmethod
from typing import Any

from core.pagination import LimitOffsetPagination, get_paginated_response
from core.services import query_or_404
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from issues.models import IssueAttachment
from issues.serializers.attachments import AttachmentDetailSerializer, AttachmentListSerializer
from issues.services.command_attachment import attachment_add_to_comment, attachment_add_to_issue, attachment_remove
from issues.services.exceptions import CommentActionNotPermitted, IssueActionNotPermitted
from issues.services.query_attachment import attachment_get, attachment_list_for_comment, attachment_list_for_issue
from issues.services.query_comment import comment_get
from issues.services.query_issue import issue_get
from rest_framework import serializers, status, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response


class BaseAttachmentListView(ABC, views.APIView):
    class Pagination(LimitOffsetPagination):
        pass

    class FilterSerializer(serializers.Serializer):
        extension = serializers.CharField(required=False)

    pagination_class = Pagination
    parser_classes = (MultiPartParser, JSONParser)

    @abstractmethod
    def get_attachments(
        self, user: AbstractBaseUser, filters: dict[str, Any], **kwargs: Any
    ) -> QuerySet[IssueAttachment]: ...

    @extend_schema(
        parameters=[FilterSerializer],
        responses=AttachmentListSerializer(many=True),
    )
    def get(self, request: Request, **kwargs: Any) -> Response:
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        attachments = self.get_attachments(**kwargs, user=request.user, filters=filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=AttachmentListSerializer,
            queryset=attachments,
            request=request,
            view=self,
        )


class IssueAttachmentListCreateView(BaseAttachmentListView):
    def get_attachments(
        self, user: AbstractBaseUser, filters: dict[str, Any], **kwargs: Any
    ) -> QuerySet[IssueAttachment]:
        return attachment_list_for_issue(issue_id=kwargs.get("issue_id"), user=user, filters=filters)

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary"},
                },
            }
        },
        responses={201: AttachmentDetailSerializer},
    )
    def post(self, request: Request, issue_id: int) -> Response:
        issue = query_or_404(issue_get, issue_id=issue_id, user=self.request.user)

        new_attachment = attachment_add_to_issue(
            file=request.FILES.get("file"), uploaded_by=self.request.user, issue=issue
        )

        data = AttachmentDetailSerializer(new_attachment).data
        return Response(data, status=status.HTTP_201_CREATED)


class CommentAttachmentListCreateView(BaseAttachmentListView):
    def get_attachments(
        self, user: AbstractBaseUser, filters: dict[str, Any], **kwargs: Any
    ) -> QuerySet[IssueAttachment]:
        return attachment_list_for_comment(
            issue_id=kwargs.get("issue_id"), comment_id=kwargs.get("comment_id"), user=user, filters=filters
        )

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary"},
                },
            }
        },
        responses={201: AttachmentDetailSerializer},
    )
    def post(self, request: Request, issue_id: int, comment_id: int) -> Response:
        comment = query_or_404(comment_get, comment_id=comment_id, issue_id=issue_id, user=self.request.user)

        new_attachment = attachment_add_to_comment(
            file=request.FILES.get("file"), uploaded_by=self.request.user, comment=comment
        )

        data = AttachmentDetailSerializer(new_attachment).data
        return Response(data, status=status.HTTP_201_CREATED)


class AttachmentDetailDeleteView(views.APIView):
    @extend_schema(responses=AttachmentDetailSerializer)
    def get(self, request: Request, issue_id: int, attachment_id: int) -> Response:
        attachment = query_or_404(
            attachment_get, issue_id=issue_id, attachment_id=attachment_id, user=self.request.user
        )

        data = AttachmentDetailSerializer(attachment).data
        return Response(data)

    @extend_schema(responses={204: None})
    def delete(self, request: Request, issue_id: int, attachment_id: int) -> Response:
        attachment = query_or_404(
            attachment_get, issue_id=issue_id, attachment_id=attachment_id, user=self.request.user
        )

        try:
            attachment_remove(attachment=attachment, requestor=self.request.user)
        except (IssueActionNotPermitted, CommentActionNotPermitted) as e:
            raise PermissionDenied(str(e)) from e

        return Response(status=status.HTTP_204_NO_CONTENT)
