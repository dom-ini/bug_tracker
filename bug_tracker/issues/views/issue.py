from core.exceptions import Conflict, Unprocessable
from core.pagination import LimitOffsetPagination, get_paginated_response
from core.serializers import CommaSeparatedMultipleChoiceField
from core.services import query_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from issues.filters import IssueOrdering
from issues.models import Issue
from issues.serializers.issue import (
    IssueAssignSerializer,
    IssueCreateSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    IssueUpdateSerializer,
)
from issues.services.command_issue import issue_assign, issue_create, issue_remove, issue_update
from issues.services.exceptions import (
    AssigneeDoesNotExistWithinProject,
    IssueActionNotPermitted,
    IssueAlreadyAssignedToGivenAssignee,
)
from issues.services.query_issue import issue_get, issue_list
from projects.services.query_project import project_get
from rest_framework import serializers, status, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response


class IssueListCreateView(views.APIView):
    class Pagination(LimitOffsetPagination):
        pass

    class FilterSerializer(serializers.Serializer):
        title = serializers.CharField(required=False, help_text=_("Case-insensitive substring filter."))
        status = serializers.ChoiceField(choices=Issue.Status.choices, required=False)
        priority = serializers.ChoiceField(choices=Issue.Priority.choices, required=False)
        type = serializers.ChoiceField(choices=Issue.Type.choices, required=False)
        assigned_to = serializers.IntegerField(required=False)
        created_by = serializers.IntegerField(required=False)
        order_by = CommaSeparatedMultipleChoiceField(choices=IssueOrdering.fields, required=False)
        unassigned = serializers.BooleanField(
            required=False, help_text=_("Return only the issues that are not assigned to any user.")
        )

    pagination_class = Pagination

    @extend_schema(
        parameters=[FilterSerializer],
        responses=IssueListSerializer(many=True),
    )
    def get(self, request: Request, project_id: int) -> Response:
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        issues = issue_list(project_id=project_id, user=request.user, filters=filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=IssueListSerializer,
            queryset=issues,
            request=request,
            view=self,
        )

    @extend_schema(request=IssueCreateSerializer, responses={201: IssueDetailSerializer})
    def post(self, request: Request, project_id: int) -> Response:
        serializer = IssueCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = query_or_404(project_get, project_id=project_id, user=self.request.user)

        try:
            new_issue = issue_create(**serializer.validated_data, created_by=self.request.user, project=project)
        except AssigneeDoesNotExistWithinProject as e:
            raise Unprocessable(str(e)) from e
        except IssueActionNotPermitted as e:
            raise PermissionDenied(str(e)) from e

        data = IssueDetailSerializer(new_issue).data
        return Response(data, status=status.HTTP_201_CREATED)


class IssueDetailUpdateDeleteView(views.APIView):
    @extend_schema(responses=IssueDetailSerializer)
    def get(self, request: Request, issue_id: int) -> Response:
        issue = query_or_404(issue_get, issue_id=issue_id, user=self.request.user)

        data = IssueDetailSerializer(issue).data
        return Response(data)

    @extend_schema(responses={204: None})
    def delete(self, request: Request, issue_id: int) -> Response:
        issue = query_or_404(issue_get, issue_id=issue_id, user=self.request.user)

        try:
            issue_remove(issue=issue, editor=self.request.user)
        except IssueActionNotPermitted as e:
            raise PermissionDenied(str(e)) from e

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=IssueUpdateSerializer, responses=IssueDetailSerializer)
    def put(self, request: Request, issue_id: int) -> Response:
        serializer = IssueUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        issue = query_or_404(issue_get, issue_id=issue_id, user=self.request.user)

        try:
            updated_issue = issue_update(issue=issue, editor=self.request.user, **serializer.validated_data)
        except IssueActionNotPermitted as e:
            raise PermissionDenied(str(e)) from e

        data = IssueDetailSerializer(updated_issue).data
        return Response(data)


class IssueAssignView(views.APIView):
    @extend_schema(request=IssueAssignSerializer, responses=IssueDetailSerializer)
    def put(self, request: Request, issue_id: int) -> Response:
        serializer = IssueAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        issue = query_or_404(issue_get, issue_id=issue_id, user=self.request.user)

        try:
            updated_issue = issue_assign(issue=issue, editor=self.request.user, **serializer.validated_data)
        except AssigneeDoesNotExistWithinProject as e:
            raise Unprocessable(str(e)) from e
        except IssueActionNotPermitted as e:
            raise PermissionDenied(str(e)) from e
        except IssueAlreadyAssignedToGivenAssignee as e:
            raise Conflict(str(e)) from e

        data = IssueDetailSerializer(updated_issue).data
        return Response(data)
