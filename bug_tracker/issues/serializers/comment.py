from issues.serializers.shared import IssueParticipantSerializer
from rest_framework import serializers


class CommentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author = IssueParticipantSerializer()
    text = serializers.CharField()
    created_at = serializers.DateTimeField()


class CommentDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author = IssueParticipantSerializer()
    text = serializers.CharField()
    created_at = serializers.DateTimeField()


class CommentCreateSerializer(serializers.Serializer):
    text = serializers.CharField()


class CommentUpdateSerializer(serializers.Serializer):
    text = serializers.CharField()
