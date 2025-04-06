from projects.models import Project, ProjectRole
from rest_framework import serializers


class ProjectDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    url = serializers.URLField()
    role = serializers.ChoiceField(choices=ProjectRole.choices)
    status = serializers.ChoiceField(choices=Project.Status.choices)


class ProjectDetailWithoutRoleSerializer(ProjectDetailSerializer):
    role = None


class ProjectListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    url = serializers.URLField()
    role = serializers.ChoiceField(choices=ProjectRole.choices)
    status = serializers.ChoiceField(choices=Project.Status.choices)


class ProjectCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    subdomain = serializers.CharField()


class ProjectUpdateSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    subdomain = serializers.CharField()
    status = serializers.ChoiceField(choices=Project.Status.choices)
