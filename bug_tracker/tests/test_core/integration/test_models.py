import pytest
from core.models import DummyModel
from django.core.exceptions import ValidationError

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_instance_has_created_and_updated_fields_after_save() -> None:
    instance = DummyModel(name="x")

    assert instance.created_at is None
    assert instance.updated_at is None

    instance.save()

    assert instance.created_at is not None
    assert instance.updated_at is not None


def test_validate_and_save_valid_instance_should_pass() -> None:
    name = "x"
    instance = DummyModel(name=name)

    instance.validate_and_save()

    assert instance.pk is not None
    assert instance.name == name


def test_validate_and_save_invalid_instance_should_fail() -> None:
    instance = DummyModel(name="x" * 2)

    with pytest.raises(ValidationError):
        instance.validate_and_save()
