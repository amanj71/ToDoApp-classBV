# from celery import shared_task
from django.apps import apps
from django.core.management import call_command
from django.db import connection
from django.conf import settings
from django.db.migrations.executor import MigrationExecutor
from django.contrib.auth import get_user_model

from typing import Any
import logging

from .db.db_schemas import use_public_schema, use_tenant_schema

logger = logging.getLogger(__name__)

## create migration functions here
# @shared_task
def migrate_public_schema_task():
    with use_public_schema():
        call_command("migrate", interactive=False)


# @shared_task  ----> this version of function is improved by ChatGPT -- original is it bottom
def migrate_tenant_task(tenant_id: str):
    Tenant = apps.get_model("tenant", "Tenant")
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        print(f"Tenant {tenant_id} does not exist. Skipping migration!!!")
        logger.error(f"Tenant {tenant_id} does not exist. Skipping migration!!!")
        return
    except Exception as e:
        print(f"Failed to get tenant {tenant_id}: {e}")
        logger.error(f"Failed to get tenant {tenant_id}: {e}")
        return

    schema_name = tenant.schema_name

    with use_tenant_schema(schema_name, create_if_missing=True):
        # The connection is now using the tenant schema.
        executor = MigrationExecutor(connection)
        loader = executor.loader
        loader.build_graph()

        # Get the labels of applications whose migrations
        # should be applied to tenant schemas.
        customer_app_labels = {app_config.label for app_config in apps.get_app_configs()
            if app_config.name in getattr(settings, "CUSTOMER_INSTALLED_APPS", [],)} 

        # Get the latest migration (leaf) of each customer app.
        leaf_nodes = [node for node in loader.graph.leaf_nodes()
            if node[0] in customer_app_labels]

        if not leaf_nodes:
            print("No customer migrations found.")
            logger.info("No customer migrations found.")
            return

        # Let Django calculate the complete migration plan,
        # including dependencies between apps.
        plan = executor.migration_plan(leaf_nodes)
        pending_migrations = [migration for migration, backwards in plan if not backwards]

        if not pending_migrations:
            print(f"Tenant '{schema_name}' is already up to date.")
            logger.info(f"Tenant '{schema_name}' is already up to date.")
            return

        print(f"Applying migrations for tenant '{schema_name}':")
        logger.info(f"Applying migrations for tenant '{schema_name}':")

        for migration in pending_migrations:
            print(f"  - {migration.app_label}.{migration.name}")
            logger.info(f"  - {migration.app_label}.{migration.name}")

        # Apply all required migrations in one operation.
        try:
            executor.migrate(leaf_nodes)
            print(f"Tenant '{schema_name}' migration completed.")
            logger.info(f"Tenant '{schema_name}' migration completed.")
            migration_succeeded = True
        except Exception as e:
            print(f"Failed to migrate tenant '{schema_name}': {e}")
            logger.error(f"Failed to migrate tenant '{schema_name}': {e}")
        #create a super user at the end of tenant migration
        if migration_succeeded and not tenant.schema_created:
            create_tenant_superuser(tenant)
    # apply schema_created field of tenant model to True after complete migrations
    if not tenant.schema_created:
        tenant.schema_created = True
        tenant.save(update_fields=["schema_created"])

# @shared_task
def migrate_tenant_schemas_task():
    Tenant = apps.get_model("tenant", "Tenant")
    with use_public_schema():
        tenant_ids = list(Tenant.objects.values_list('id', flat=True))
        call_command("migrate", interactive=False)
    failed = []
    for tenant_id in tenant_ids:
        try:
            migrate_tenant_task(tenant_id)
        except Exception:
            logger.exception(f"Migration failed for tenant {tenant_id}")
            failed.append(tenant_id)

    if failed:
        logger.error(f"{len(failed)} tenant(s) failed migration: {failed}")
    return failed  # optional, but useful if this is called from a Celery task wrapper that wants the result


def create_tenant_superuser(tenant):
    User = get_user_model()
    schema_name = tenant.schema_name
    if User.objects.filter(email=tenant.owner_email).exists():
        logger.info(f"[{schema_name}] Superuser for {tenant.owner_email} already exists, skipping.")
        return
    User.objects.create_superuser(
        username=tenant.name,   
        email=tenant.owner_email,
        password='Zxc123456!',
    )
    logger.info(f"[{schema_name}] Superuser created for {tenant.owner_email}")



### Original migrate_tenant_task function by cfe
# def migrate_tenant_task(tenant_id:str):
#     Tenant = apps.get_model("tenant", "Tenant")
#     try:
#         instance = Tenant.objects.get(id=tenant_id)
#     except Exception as e:
#         print(f'Tenant {tenant_id} failed: {e}')
#         return
#     schema_name = instance.schema_name
#     with use_tenant_schema(schema_name, create_if_missing=True):
#         # Initialize the executor after setting the search path
#         executor = MigrationExecutor(connection)
#         loader = executor.loader
#         loader.build_graph()  # Ensure the graph is up-to-date

#         customer_apps = getattr(settings, 'INSTALLED_APPS', [])
#         customer_app_configs = [
#             app_config for app_config in apps.get_app_configs()
#             if app_config.name in customer_apps
#         ]

#         # For each customer app, determine what migrations need to be run
#         for app_config in customer_app_configs:
#             app_label = app_config.label

#             # Get all leaf nodes for this app
#             leaf_nodes = [
#                 node for node in loader.graph.leaf_nodes()
#                 if node[0] == app_label
#             ]

#             if not leaf_nodes:
#                 # App has no migrations at all, do nothing silently
#                 continue

#             # For each leaf node, figure out the plan to get there
#             # If the plan is empty, it means no new migrations are needed.
#             full_plan = []
#             for leaf in leaf_nodes:
#                 plan = executor.migration_plan([leaf])
#                 for migration, backwards in plan:
#                     if not backwards:  # only include forward migrations
#                         full_plan.append(migration)

#             # Remove duplicates while preserving order
#             seen = set()
#             ordered_migrations = []
#             for m in full_plan:
#                 if m not in seen:
#                     seen.add(m)
#                     ordered_migrations.append(m)

#             if not ordered_migrations:
#                 # No forward migrations needed for this app
#                 continue

#             # Print out which migrations are going to be applied
#             print(f"Applying migrations for '{app_label}':")
#             for migration in ordered_migrations:
#                 print(f"  - {migration.app_label}.{migration.name}")

#             # Apply the migrations
#             # The plan to migrate is the leaf_nodes for this app
#             executor.migrate(leaf_nodes)
#             # Rebuild the graph after applying migrations
#             executor.loader.build_graph()

