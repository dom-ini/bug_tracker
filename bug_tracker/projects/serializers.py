from django.conf import settings
from django.utils.translation import gettext_lazy as _
from projects.models import Project
from projects.services.projects import is_subdomain_change_allowed
from rest_framework import serializers


class CommonProjectSerializerMixin(serializers.ModelSerializer):
    role = serializers.SerializerMethodField(method_name="get_role")

    def get_role(self, obj: Project) -> str:
        user = self.context["request"].user
        return obj.get_user_role(user)


class ProjectListSerializer(CommonProjectSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name", "url", "role", "status")
        read_only_fields = ("id", "name", "url", "role", "status")


class ProjectDetailSerializer(CommonProjectSerializerMixin, serializers.ModelSerializer):
    def validate_subdomain[SubdomainT](self, value: SubdomainT) -> SubdomainT:
        is_change_allowed, next_allowed_change = is_subdomain_change_allowed(self.instance)
        if not is_change_allowed:
            raise serializers.ValidationError(
                _(
                    "Subdomain can only be changed every %(interval)d days. "
                    "Next change possible on: %(next_allowed)s"
                    % {
                        "interval": settings.SUBDOMAIN_CHANGE_INTERVAL_DAYS,
                        "next_allowed": next_allowed_change.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
            )
        return value

    class Meta:
        model = Project
        fields = ("id", "name", "description", "url", "role", "status")
        read_only_fields = ("id", "name", "description", "url", "role", "status")


class ProjectCreateSerializer(CommonProjectSerializerMixin, serializers.ModelSerializer):
    subdomain = serializers.CharField(write_only=True)

    class Meta:
        model = Project
        fields = ("id", "name", "description", "subdomain", "url", "role", "status")
        read_only_fields = ("id", "role", "status", "url")


class ProjectEditSerializer(CommonProjectSerializerMixin, serializers.ModelSerializer):
    subdomain = serializers.CharField(write_only=True)

    class Meta:
        model = Project
        fields = ("id", "name", "description", "subdomain", "url", "role", "status")
        read_only_fields = ("id", "role", "url")
