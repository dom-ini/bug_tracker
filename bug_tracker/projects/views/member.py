from core.exceptions import Conflict
from core.pagination import LimitOffsetPagination, get_paginated_response
from core.serializers import CommaSeparatedMultipleChoiceField
from core.services import query_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from projects.filters import MemberOrdering
from projects.models import ProjectRole
from projects.serializers.member import MemberCreateSerializer, MemberDetailSerializer, MemberUpdateSerializer
from projects.services.command_member import (
    member_add_to_project,
    member_change_role_in_project,
    member_remove_from_project,
)
from projects.services.exceptions import (
    MemberAlreadyInProject,
    NotSufficientRoleInProject,
    UserCannotModifyOwnMembership,
)
from projects.services.query_member import member_get, member_list
from projects.services.query_project import project_get
from rest_framework import serializers, status, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response


class MemberListCreateView(views.APIView):
    class Pagination(LimitOffsetPagination):
        pass

    class FilterSerializer(serializers.Serializer):
        first_name = serializers.CharField(required=False, help_text=_("Case-insensitive substring filter."))
        last_name = serializers.CharField(required=False, help_text=_("Case-insensitive substring filter."))
        email = serializers.CharField(required=False, help_text=_("Case-insensitive substring filter."))
        role = serializers.ChoiceField(choices=ProjectRole.choices, required=False)
        order_by = CommaSeparatedMultipleChoiceField(choices=MemberOrdering.fields, required=False)

    pagination_class = Pagination

    @extend_schema(
        parameters=[FilterSerializer],
        responses=MemberDetailSerializer(many=True),
    )
    def get(self, request: Request, project_id: int) -> Response:
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        members = member_list(project_id=project_id, user=request.user, filters=filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=MemberDetailSerializer,
            queryset=members,
            request=request,
            view=self,
        )

    @extend_schema(request=MemberCreateSerializer, responses={201: MemberDetailSerializer})
    def post(self, request: Request, project_id: int) -> Response:
        serializer = MemberCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = query_or_404(project_get, project_id=project_id, user=self.request.user)

        try:
            new_member_id = member_add_to_project(
                **serializer.validated_data, editor=self.request.user, project=project
            ).user_id
        except NotSufficientRoleInProject as e:
            raise PermissionDenied(str(e)) from e
        except MemberAlreadyInProject as e:
            raise Conflict(str(e)) from e

        new_member = member_get(project_id=project_id, member_id=new_member_id, user=self.request.user)
        data = MemberDetailSerializer(new_member).data
        return Response(data, status=status.HTTP_201_CREATED)


class MemberDetailUpdateDeleteView(views.APIView):
    @extend_schema(responses=MemberDetailSerializer)
    def get(self, request: Request, project_id: int, member_id: int) -> Response:
        member = query_or_404(member_get, project_id=project_id, member_id=member_id, user=self.request.user)

        data = MemberDetailSerializer(member).data
        return Response(data)

    @extend_schema(responses={204: None})
    def delete(self, request: Request, project_id: int, member_id: int) -> Response:
        project = query_or_404(project_get, project_id=project_id, user=self.request.user)
        member = query_or_404(member_get, project_id=project_id, member_id=member_id, user=self.request.user)

        try:
            member_remove_from_project(project=project, editor=self.request.user, member=member)
        except (NotSufficientRoleInProject, UserCannotModifyOwnMembership) as e:
            raise PermissionDenied(str(e)) from e

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=MemberUpdateSerializer, responses=MemberDetailSerializer)
    def put(self, request: Request, project_id: int, member_id: int) -> Response:
        serializer = MemberUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        project = query_or_404(project_get, project_id=project_id, user=self.request.user)
        member = query_or_404(member_get, project_id=project_id, member_id=member_id, user=self.request.user)

        try:
            updated_member = member_change_role_in_project(
                project=project, editor=self.request.user, member=member, **serializer.validated_data
            )
        except (NotSufficientRoleInProject, UserCannotModifyOwnMembership) as e:
            raise PermissionDenied(str(e)) from e

        data = MemberDetailSerializer(updated_member).data
        return Response(data)
