from django.apps import apps
from django.db import connection
from contextlib import contextmanager

from . import sql_statements

DEFAULT_SCHEMA = "public"

def check_if_schema_exists(schema_name, required_check=False):
    if schema_name == DEFAULT_SCHEMA and not required_check:
        return True
    exists = False
    with connection.cursor() as cursor:
        cursor.execute("""SELECT schema_name FROM information_schema.schemata 
        WHERE schema_name = %s""", [schema_name])
        exists = cursor.fetchone() is not None 
    return exists

def activate_tenant_schema(schema_name):
    is_check_exists_required = schema_name != DEFAULT_SCHEMA
    schema_to_use = DEFAULT_SCHEMA
    if is_check_exists_required and check_if_schema_exists(schema_name):
        schema_to_use = schema_name
    with connection.cursor() as cursor:
        sql = f'SET search_path TO "{schema_to_use}";'
        cursor.execute(sql)
        connection.schema_name = schema_to_use

@contextmanager
def use_tenant_schema(schema_name, create_if_missing=True):
    """
    with use_tenant_schema(schema_name):
        Visit.object.all()
    """
    previous_schema = getattr(connection, "schema_name", DEFAULT_SCHEMA)
    try:
        if create_if_missing and not check_if_schema_exists(schema_name):
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}";')
        activate_tenant_schema(schema_name)
        yield

    finally:
        activate_tenant_schema(previous_schema)


@contextmanager
def use_public_schema():
    """
    with use_public_schema():
        Tenant.object.all()
    """
    previous_schema = connection.schema_name
    try:
        if previous_schema != DEFAULT_SCHEMA:
            activate_tenant_schema(DEFAULT_SCHEMA)
        yield

    finally:
        if previous_schema != DEFAULT_SCHEMA:
            activate_tenant_schema(previous_schema)

