from django.core.management import BaseCommand

from typing import Any

from ... import tasks

class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any):
        self.stdout.write("Starting migrations")
        tasks.migrate_tenant_schemas_task()
        self.stdout.write(self.style.SUCCESS("All migrations for CUSTOMER_APPS are completed."))