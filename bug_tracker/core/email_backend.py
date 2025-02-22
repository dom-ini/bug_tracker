from typing import Sequence

from core.emails import serialize_email_messages
from core.tasks import async_send_messages
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend


class AsyncEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages: Sequence[EmailMessage]) -> int:
        serialized_messages = serialize_email_messages(email_messages)
        async_send_messages.delay(serialized_messages)
        return len(email_messages)
