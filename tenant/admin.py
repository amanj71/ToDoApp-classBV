from django.contrib import admin

from .models import Tenant, Domain
from helpers.adminpanelmixin import TenantScopedAdminMixin

## Register your models here.
class TenantAdmin(TenantScopedAdminMixin, admin.ModelAdmin):
    readonly_fields = ['schema_name', 'schema_created', 'created_on']

class DomainAdmin(TenantScopedAdminMixin, admin.ModelAdmin):
    list_display = ['domain', 'tenant']


## show models in admin panel
admin.site.register(Tenant, TenantAdmin)
admin.site.register(Domain, DomainAdmin)

