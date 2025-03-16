from core.filters import BaseOrdering
from django_filters import rest_framework as filters
from projects.models import Project


class ProjectOrdering(BaseOrdering):
    base_fields = ["name", "status", "role"]


class ProjectFilter(filters.FilterSet):
    role = filters.CharFilter(field_name="role", lookup_expr="exact")
    order_by = filters.OrderingFilter(fields=ProjectOrdering.base_fields)

    class Meta:
        model = Project
        fields = {
            "name": ["icontains"],
            "status": ["exact"],
        }


class MemberOrdering(BaseOrdering):
    base_fields = ["first_name", "last_name", "email", "role"]


class MemberFilter(filters.FilterSet):
    first_name = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    email = filters.CharFilter(field_name="email", lookup_expr="icontains")
    role = filters.CharFilter(field_name="role", lookup_expr="exact")
    order_by = filters.OrderingFilter(fields=MemberOrdering.base_fields)
