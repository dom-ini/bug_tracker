from rest_framework import serializers


class IssueParticipantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
