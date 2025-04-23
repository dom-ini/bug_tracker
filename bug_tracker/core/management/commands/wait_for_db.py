import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.utils import OperationalError


def get_default_db_connection() -> BaseDatabaseWrapper:
    return connections["default"]


class Command(BaseCommand):
    help = "Wait for database to be available"

    def handle(self, *args, **kwargs) -> None:
        self.stdout.write("Waiting for database...")
        db_conn: BaseDatabaseWrapper | None = None
        while not db_conn:
            try:
                db_conn = get_default_db_connection()
                self.stdout.write(self.style.SUCCESS("Database is ready!"))
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 5 seconds...")
                time.sleep(5)
