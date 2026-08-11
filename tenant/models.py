from django.db import models, connection
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

from . import utils
from helpers import tasks
from helpers.db import sql_statements

## Create your models here.


# PostgreSQL schema name rules: lowercase letters, digits, underscores;
# must start with a letter; keep it short to avoid identifier length issues.
RESERVED_SCHEMA_NAMES = {
    'public', 'information_schema', 'pg_catalog', 'pg_toast',
    'admin', 'www', 'api', 'static', 'media',
}

class Tenant(models.Model):
    class Status(models.TextChoices):
        TRIAL = 'trial', 'Trial'
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'
        CANCELLED = 'cancelled', 'Cancelled'

    # --- Identity ---
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, db_index=True, editable=False)
    name = models.CharField(max_length=255)  # human-readable/company name
    schema_name = models.CharField(max_length=60, unique=True, db_index=True, editable=False,
                                   blank=True, null=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True, null=True)

    # --- Ownership / contact ---
    owner_email = models.EmailField()
    # (If tenants map 1:1 to a User created in the public schema, use a FK instead.)

    # --- Lifecycle / billing ---
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIAL)
    is_active = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=True)
    is_paid_plan = models.BooleanField(default=False)
    paid_until = models.DateTimeField(null=True, blank=True)

    # --- Provisioning bookkeeping ---
    schema_created = models.BooleanField(default=False)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # --- Soft delete ---
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'public.tenants'  # explicit: this table itself lives in `public`
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.name} ({self.schema_name})"

    # ---------- Validation ----------
    def clean(self):
        if self.schema_name in RESERVED_SCHEMA_NAMES:
            raise ValidationError({'schema_name': 'This schema name is reserved.'})

    # ---------- Status transitions ----------
    def activate(self):
        self.is_active = True
        self.status = self.Status.ACTIVE
        self.deactivated_at = None
        self.save(update_fields=['is_active', 'status', 'deactivated_at'])

    def deactivate(self):
        self.is_active = False
        self.status = self.Status.SUSPENDED
        self.deactivated_at = timezone.now()
        self.save(update_fields=['is_active', 'status', 'deactivated_at'])

    def extend_trial(self, days=14):
        base = self.trial_ends_at or timezone.now()
        self.trial_ends_at = base + timezone.timedelta(days=days)
        self.save(update_fields=['trial_ends_at'])

    @property
    def is_trial_expired(self):
        return bool(self.trial_ends_at and timezone.now() > self.trial_ends_at)

    @property
    def is_paid_active(self):
        return bool(self.paid_until and timezone.now() < self.paid_until)

    def save(self, *args, **kwargs):
        created = False
        if not self.pk:
            created = True
        now = timezone.now()
        
        if not self.schema_name:
            self.schema_name = utils.generate_unique_schema_name(self.id, self.name) # utils created by me & should be imported
        # force fields not to change in model level
        if not self._state.adding:
            old_obj = Tenant.objects.get(id=self.pk)
            self.schema_name = old_obj.schema_name
            self.created_on = old_obj.created_on

        super().save(*args, **kwargs)
        # execute below func to automatically migrate new created tenant by this model
        tasks.migrate_tenant_task(self.id)


class Domain(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    domain = models.CharField(max_length=110, unique=True, db_index=True)
    # marks the canonical domain when a tenant has more than one custom domain + default subdomain, staging alias, etc.)
    is_primary = models.BooleanField(default=True)
    # relevant once you support custom domains (not subdomains) —
    # you'd need DNS/TXT-record verification before routing traffic there safely
    is_verified = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'public.domains'
        ordering = ['-is_primary', '-created_on']
        constraints = [
            # enforces at the DB level that a tenant can only have one primary domain at a time,
            # rather than trusting application code alone.
            models.UniqueConstraint(fields=['tenant'], condition=models.Q(is_primary=True),
                name='unique_primary_domain_per_tenant',)
        ]

    def __str__(self):
        return self.domain

    def make_primary(self):
        """Demote any other primary domain for this tenant, then promote this one."""
        Domain.objects.filter(tenant=self.tenant, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        self.is_primary = True
        self.save(update_fields=['is_primary'])