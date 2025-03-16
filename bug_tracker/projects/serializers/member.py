from projects.models import ProjectRole
from rest_framework import serializers


class MemberDetailSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    role = serializers.ChoiceField(choices=ProjectRole.choices)


class MemberCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=ProjectRole.choices)


class MemberUpdateSerializer(serializers.Serializer):
    new_role = serializers.ChoiceField(choices=ProjectRole.choices)
