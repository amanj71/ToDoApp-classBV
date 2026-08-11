from django.apps import apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.core.cache import cache
import logging

from ..db import sql_statements
from ..db.db_schemas import use_public_schema, activate_tenant_schema

logger = logging.getLogger(__name__)

class TenantSchemaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
    def __call__(self, request):
        # simply get your url by get_host() method in request
        host = request.get_host()
        host_portless = host.split(':')[0]
        host_split = host_portless.split('.')
        subdomin = None
        if len(host_split) > 1:
            subdomin = host_split[0]
        schema_name, tenant_active = self.get_schema_name(subdomain=subdomin)
        activate_tenant_schema(schema_name)
        request.tenant_active = tenant_active
        return self.get_response(request)

    def get_schema_name(self, subdomain=None):
        if subdomain in [None, 'localhost', '127']:
            return 'public', True

        cache_domain_key = f"subdomain_schema:{subdomain}"
        cache_active_key = f"subdomain_valid_schema:{subdomain}"
        cached_schema = cache.get(cache_domain_key)
        cached_active = cache.get(cache_active_key)

        if cached_schema is not None and cached_active is not None:
            return cached_schema, cached_active

        schema_name = "public"
        tenant_active = False

        with use_public_schema():
            Domain = apps.get_model('tenant', 'Domain')
            try:
                domain_obj = Domain.objects.select_related('tenant').get(domain=subdomain)
                tenant = domain_obj.tenant
                if tenant.is_active and tenant.schema_created and tenant.schema_name:
                    schema_name = tenant.schema_name
                    tenant_active = True
                else:
                    logger.info(
                        f"Tenant for '{subdomain}' found but not routable "
                        f"(is_active={tenant.is_active}, schema_created={tenant.schema_created})"
                    )
            except Domain.DoesNotExist:
                logger.info(f"No domain match for subdomain '{subdomain}'")

            cache_ttl = 60
            cache.set(cache_domain_key, str(schema_name), cache_ttl)
            cache.set(cache_active_key, tenant_active, cache_ttl)

        return schema_name, tenant_active
