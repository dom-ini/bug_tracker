from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import Direction
from rest_framework import serializers


class CustomAutoSchema(AutoSchema):
    def get_serializer_name(self, serializer: serializers.Serializer, direction: Direction) -> str:
        view_name = self.view.__class__.__name__
        return f"{view_name}.{serializer.__class__.__name__}"
