# helpers/admin_mixins.py
from django.apps import apps as django_apps
from django.conf import settings
from django.db import connection


def is_public_schema():
    return getattr(connection, "schema_name", "public") == "public"


def model_allowed_in_current_schema(model):
    app_config = django_apps.get_app_config(model._meta.app_label)
    customer_apps = set(getattr(settings, "CUSTOMER_INSTALLED_APPS", []))

    if is_public_schema():
        # public-schema apps only (e.g. `tenant`, `domain`) — adjust to your split
        return app_config.name not in customer_apps
    else:
        # tenant schema — only customer apps are valid here
        return app_config.name in customer_apps


class TenantScopedAdminMixin:
    def has_module_permission(self, request):
        if not model_allowed_in_current_schema(self.model):
            return False
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        if not model_allowed_in_current_schema(self.model):
            return False
        return super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        if not model_allowed_in_current_schema(self.model):
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if not model_allowed_in_current_schema(self.model):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not model_allowed_in_current_schema(self.model):
            return False
        return super().has_delete_permission(request, obj)