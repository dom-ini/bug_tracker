from issues.models import Issue
from issues.templates.serializers.shared import IssueParticipantSerializer
from rest_framework import serializers


class IssueListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    status = serializers.ChoiceField(choices=Issue.Status.choices)
    priority = serializers.ChoiceField(choices=Issue.Priority.choices)
    type = serializers.ChoiceField(choices=Issue.Type.choices)
    created_by = IssueParticipantSerializer()
    assigned_to = IssueParticipantSerializer()
    created_at = serializers.DateTimeField()


class IssueDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    project_id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    status = serializers.ChoiceField(choices=Issue.Status.choices)
    priority = serializers.ChoiceField(choices=Issue.Priority.choices)
    type = serializers.ChoiceField(choices=Issue.Type.choices)
    created_by = IssueParticipantSerializer()
    assigned_to = IssueParticipantSerializer()
    created_at = serializers.DateTimeField()


class IssueCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    priority = serializers.ChoiceField(choices=Issue.Priority.choices)
    issue_type = serializers.ChoiceField(choices=Issue.Type.choices)
    assigned_to_id = serializers.IntegerField(allow_null=True)


class IssueUpdateSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    status = serializers.ChoiceField(choices=Issue.Status.choices)
    priority = serializers.ChoiceField(choices=Issue.Priority.choices)
    issue_type = serializers.ChoiceField(choices=Issue.Type.choices)


class IssueAssignSerializer(serializers.Serializer):
    assigned_to_id = serializers.IntegerField(allow_null=True)
