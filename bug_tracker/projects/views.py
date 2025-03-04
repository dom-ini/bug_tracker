from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from projects.filters import ProjectFilter
from projects.models import Project
from projects.permissions import CanEditProject
from projects.project_resolver import MissingProjectIdentifierHeader, resolve_project_from_header
from projects.serializers.project import (
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectEditSerializer,
    ProjectListSerializer,
)
from projects.services.project import project_create, project_update
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class ProjectViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    filterset_class = ProjectFilter
    ordering_fields = ["name", "role", "status"]
    permission_classes = [IsAuthenticated, CanEditProject]

    @extend_schema(
        parameters=[OpenApiParameter(name=settings.SUBDOMAIN_HEADER_NAME, type=str, location=OpenApiParameter.HEADER)]
    )
    @action(detail=False)
    def current(self, request: HttpRequest) -> Response:
        queryset = self.get_queryset()
        try:
            project = resolve_project_from_header(request)
        except MissingProjectIdentifierHeader as e:
            raise NotFound(str(e))
        if project is None or not queryset.contains(project):
            raise NotFound(_("Project not found"))

        serializer = self.get_serializer(project)
        return Response(serializer.data)

    def get_queryset(self) -> QuerySet[Project]:
        if getattr(self, "swagger_fake_view", False):
            return Project.objects.all()
        queryset = Project.objects.all_by_user(self.request.user)
        return queryset

    def get_serializer_class(self) -> type[serializers.Serializer]:
        if self.action == "list":
            return ProjectListSerializer
        elif self.action == "retrieve":
            return ProjectDetailSerializer
        elif self.action == "create":
            return ProjectCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ProjectEditSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer: ProjectDetailSerializer) -> None:
        data = serializer.validated_data
        project = project_create(project_data=data, user=self.request.user)
        serializer.instance = project

    def perform_update(self, serializer: ProjectDetailSerializer) -> None:
        data = serializer.validated_data
        project = self.get_object()
        project = project_update(project=project, project_data=data)
        serializer.instance = project
