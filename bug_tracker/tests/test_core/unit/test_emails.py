import pytest
from core.emails import EmailMessageData, deserialize_email_messages, serialize_email_messages
from django.core.mail import EmailMessage

pytestmark = pytest.mark.unit


@pytest.fixture
def sample_email_message() -> EmailMessage:
    return EmailMessage(
        subject="Test Subject",
        body="Test Body",
        from_email="test@example.com",
        to=["recipient@example.com"],
        bcc=["bcc@example.com"],
        cc=["cc@example.com"],
        reply_to=["reply@example.com"],
    )


def test_from_email_message(sample_email_message: EmailMessage) -> None:
    email_data = EmailMessageData.from_email_message(sample_email_message)

    assert email_data.subject == sample_email_message.subject
    assert email_data.body == sample_email_message.body
    assert email_data.from_email == sample_email_message.from_email
    assert email_data.to == sample_email_message.to
    assert email_data.bcc == sample_email_message.bcc
    assert email_data.cc == sample_email_message.cc
    assert email_data.reply_to == sample_email_message.reply_to


def test_to_email_message(sample_email_message: EmailMessage) -> None:
    email_data = EmailMessageData.from_email_message(sample_email_message)
    converted_message = email_data.to_email_message()

    assert isinstance(converted_message, EmailMessage)
    assert converted_message.subject == sample_email_message.subject
    assert converted_message.body == sample_email_message.body
    assert converted_message.from_email == sample_email_message.from_email
    assert converted_message.to == sample_email_message.to
    assert converted_message.bcc == sample_email_message.bcc
    assert converted_message.cc == sample_email_message.cc
    assert converted_message.reply_to == sample_email_message.reply_to


def test_serialize_email_messages(sample_email_message: EmailMessage) -> None:
    email_data_list = serialize_email_messages([sample_email_message])

    assert len(email_data_list) == 1
    assert "subject" in email_data_list[0]
    assert "body" in email_data_list[0]
    assert email_data_list[0]["subject"] == sample_email_message.subject
    assert email_data_list[0]["body"] == sample_email_message.body


def test_deserialize_email_messages(sample_email_message: EmailMessage) -> None:
    serialized_data = serialize_email_messages([sample_email_message])
    deserialized_messages = deserialize_email_messages(serialized_data)

    assert len(deserialized_messages) == 1
    assert isinstance(deserialized_messages[0], EmailMessage)
    assert deserialized_messages[0].subject == sample_email_message.subject
    assert deserialized_messages[0].body == sample_email_message.body
    assert deserialized_messages[0].from_email == sample_email_message.from_email
    assert deserialized_messages[0].to == sample_email_message.to
    assert deserialized_messages[0].bcc == sample_email_message.bcc
    assert deserialized_messages[0].cc == sample_email_message.cc
    assert deserialized_messages[0].reply_to == sample_email_message.reply_to
