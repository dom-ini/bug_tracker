from typing import Sequence

from celery.exceptions import Reject
from core.emails import deserialize_email_messages
from core.logger import get_main_logger
from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from bug_tracker.celery import app


@app.task(retry_backoff=True)
def async_send_messages(messages: Sequence[dict]) -> None:
    try:
        deserialized_messages = deserialize_email_messages(messages)
    except TypeError as e:
        get_main_logger().error(f"Failed to deserialize messages: {e}")
        raise Reject(str(e), requeue=False) from e

    conn: BaseEmailBackend = get_connection(backend=settings.CORE_EMAIL_BACKEND)
    conn.send_messages(deserialized_messages)
