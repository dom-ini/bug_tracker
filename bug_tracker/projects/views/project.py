from core.exceptions import Unprocessable
from core.pagination import LimitOffsetPagination, get_paginated_response
from core.serializers import CommaSeparatedMultipleChoiceField
from core.services import query_or_404
from django.conf import settings
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from projects.filters import ProjectOrdering
from projects.models import Project, ProjectRole
from projects.project_resolver import MissingProjectIdentifierHeader, resolve_project_from_header
from projects.selectors.project import project_get, project_list
from projects.serializers.project import (
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectDetailWithoutRoleSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer,
)
from projects.services.exceptions import NotSufficientRoleInProject, SubdomainRecentlyChanged
from projects.services.project import project_create, project_update
from rest_framework import serializers, status, views
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response


class ProjectDetailUpdateView(views.APIView):
    @extend_schema(responses=ProjectDetailSerializer)
    def get(self, request: Request, project_id: int) -> Response:
        project = query_or_404(project_get, project_id=project_id, user=self.request.user)

        data = ProjectDetailSerializer(project).data
        return Response(data)

    @extend_schema(request=ProjectUpdateSerializer, responses=ProjectDetailWithoutRoleSerializer)
    def put(self, request: Request, project_id: int) -> Response:
        serializer = ProjectUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        project = query_or_404(project_get, project_id=project_id, user=self.request.user)

        try:
            updated_project = project_update(project=project, editor=self.request.user, **serializer.validated_data)
        except NotSufficientRoleInProject as e:
            raise PermissionDenied(str(e)) from e
        except SubdomainRecentlyChanged as e:
            raise Unprocessable(str(e)) from e

        data = ProjectDetailWithoutRoleSerializer(updated_project).data
        return Response(data)


class ProjectListCreateView(views.APIView):
    class Pagination(LimitOffsetPagination):
        pass

    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False, help_text=_("Case-insensitive substring filter."))
        status = serializers.ChoiceField(choices=Project.Status.choices, required=False)
        role = serializers.ChoiceField(choices=ProjectRole.choices, required=False)
        order_by = CommaSeparatedMultipleChoiceField(choices=ProjectOrdering.fields, required=False)

    pagination_class = Pagination

    @extend_schema(
        parameters=[FilterSerializer],
        responses=ProjectListSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        projects = project_list(user=request.user, filters=filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=ProjectListSerializer,
            queryset=projects,
            request=request,
            view=self,
        )

    @extend_schema(request=ProjectCreateSerializer, responses={201: ProjectDetailWithoutRoleSerializer})
    def post(self, request: Request) -> Response:
        serializer = ProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_project = project_create(**serializer.validated_data, user=request.user)

        data = ProjectDetailWithoutRoleSerializer(new_project).data
        return Response(data, status=status.HTTP_201_CREATED)


class ProjectCurrentDetailView(views.APIView):
    @extend_schema(
        parameters=[OpenApiParameter(name=settings.SUBDOMAIN_HEADER_NAME, type=str, location=OpenApiParameter.HEADER)],
        responses=ProjectDetailSerializer,
    )
    def get(self, request: HttpRequest) -> Response:
        try:
            project = resolve_project_from_header(request)
        except MissingProjectIdentifierHeader as e:
            raise NotFound(str(e)) from e

        if project is None:
            raise NotFound(_("Project not found"))

        data = ProjectDetailSerializer(project).data
        return Response(data)
