import pytest
from core.schema import CustomAutoSchema
from rest_framework import serializers
from rest_framework.views import APIView

pytestmark = pytest.mark.unit


class DummyView(APIView):
    pass


class DummySerializer(serializers.Serializer):
    pass


def test_custom_auto_schema_get_serializer_name() -> None:
    schema = CustomAutoSchema()
    schema.view = DummyView()

    name = schema.get_serializer_name(DummySerializer(), "request")

    assert name == "DummyView.DummySerializer"
