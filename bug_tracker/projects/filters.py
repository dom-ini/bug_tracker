from django_filters import rest_framework as filters
from projects.models import Project


class ProjectFilter(filters.FilterSet):
    class Meta:
        model = Project
        fields = {
            "name": ["icontains"],
            "status": ["exact"],
        }
