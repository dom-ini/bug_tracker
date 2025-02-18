from core.emails import EmailMessageData, deserialize_email_messages
from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from bug_tracker.celery import app


@app.task(retry_backoff=True)
def async_send_messages(messages: list[EmailMessageData]) -> None:
    deserialized_messages = deserialize_email_messages(messages)
    conn: BaseEmailBackend = get_connection(backend=settings.CORE_EMAIL_BACKEND)
    conn.send_messages(deserialized_messages)
