from rest_framework import serializers


class AttachmentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.CharField()
    created_at = serializers.DateTimeField()


class AttachmentDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.CharField()
    created_at = serializers.DateTimeField()
