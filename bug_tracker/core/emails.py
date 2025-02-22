from dataclasses import asdict, dataclass
from typing import Sequence

from django.core.mail import EmailMessage


@dataclass
class EmailMessageData:
    subject: str
    body: str
    from_email: str
    to: list[str] | None = None
    bcc: list[str] | None = None
    cc: list[str] | None = None
    reply_to: list[str] | None = None

    @staticmethod
    def from_email_message(message: EmailMessage) -> "EmailMessageData":
        return EmailMessageData(
            subject=message.subject,
            body=message.body,
            from_email=message.from_email,
            to=message.to,
            bcc=message.bcc,
            cc=message.cc,
            reply_to=message.reply_to,
        )

    def to_email_message(self) -> EmailMessage:
        return EmailMessage(
            subject=self.subject,
            body=self.body,
            from_email=self.from_email,
            to=self.to,
            bcc=self.bcc,
            cc=self.cc,
            reply_to=self.reply_to,
        )


def serialize_email_messages(messages: Sequence[EmailMessage]) -> Sequence[dict]:
    return [asdict(EmailMessageData.from_email_message(message)) for message in messages]


def deserialize_email_messages(messages: Sequence[dict]) -> Sequence[EmailMessage]:
    return [EmailMessageData(**message).to_email_message() for message in messages]
