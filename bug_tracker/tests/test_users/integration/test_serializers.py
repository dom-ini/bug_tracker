from unittest.mock import Mock

import pytest
from django.core import mail
from pytest_mock import MockerFixture
from users.models import CustomUser
from users.serializers import CustomRegisterSerializer

pytestmark = pytest.mark.integration


@pytest.fixture
def dummy_request(mocker: MockerFixture) -> Mock:
    return mocker.Mock(session={})


@pytest.mark.django_db
def test_register_serializer_save_should_send_account_already_exists_mail(
    user_with_verified_email: CustomUser, dummy_request: Mock
) -> None:
    data = {
        "username": "user1",
        "email": user_with_verified_email.email,
        "first_name": "First",
        "last_name": "Last",
        "password": "P@ssword123123",
    }
    serializer = CustomRegisterSerializer(data=data)
    assert serializer.is_valid()
    assert len(mail.outbox) == 0

    new_user = serializer.save(dummy_request)

    assert new_user is None
    assert len(mail.outbox) == 1
    sent_mail = mail.outbox[0]
    assert sent_mail.to == [user_with_verified_email.email]
