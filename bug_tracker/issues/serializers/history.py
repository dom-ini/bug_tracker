from auditlog.models import LogEntry
from issues.serializers.shared import IssueParticipantSerializer
from rest_framework import serializers


class HistoryEntryListSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=LogEntry.Action.choices)
    timestamp = serializers.DateTimeField()
    content_type = serializers.CharField()
    changes = serializers.JSONField()
    actor = IssueParticipantSerializer()
