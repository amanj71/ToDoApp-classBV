from django.test import TestCase
from django.contrib.auth.models import User
from django.db import connection
from types import SimpleNamespace

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

from accounts.api.v0.serializers import UserTokenObtainSerializer
from helpers.authentication import TenantJWTAuthentication


class TenantJWTAuthenticationTests(TestCase):
    def setUp(self):
        # create a reusable user for tests
        self.user = User.objects.create_user(username='tenantuser', password='password123')

    def make_request_with_token(self, raw_token):
        # Simple request-like object used by the authentication class
        return SimpleNamespace(META={"HTTP_AUTHORIZATION": f"Bearer {raw_token}"})

    def test_token_includes_tenant_claim_and_authenticates(self):
        # Issue a token bound to a tenant schema
        connection.schema_name = 'tenant_a'
        token_obj = UserTokenObtainSerializer.get_token(self.user)
        raw_access = str(token_obj.access_token)

        request = self.make_request_with_token(raw_access)
        auth = TenantJWTAuthentication()
        user, validated_token = auth.authenticate(request)

        self.assertEqual(user.pk, self.user.pk)
        # token should contain tenant claim
        self.assertEqual(validated_token.get('tenant'), 'tenant_a')

    def test_token_cannot_be_used_on_other_tenant(self):
        # Token created for tenant_a cannot authenticate when current schema is tenant_b
        connection.schema_name = 'tenant_a'
        token_obj = UserTokenObtainSerializer.get_token(self.user)
        raw_access = str(token_obj.access_token)

        # switch active schema to another tenant
        connection.schema_name = 'tenant_b'
        request = self.make_request_with_token(raw_access)
        auth = TenantJWTAuthentication()
        with self.assertRaises(AuthenticationFailed):
            auth.authenticate(request)

    def test_legacy_token_rejected_for_nonpublic_schema(self):
        # Tokens that lack a tenant claim (legacy tokens) should be rejected for tenant schemas
        # Create a legacy token (no tenant claim injected)
        legacy_refresh = RefreshToken.for_user(self.user)
        raw_access = str(legacy_refresh.access_token)

        connection.schema_name = 'tenant_z'
        request = self.make_request_with_token(raw_access)
        auth = TenantJWTAuthentication()
        with self.assertRaises(AuthenticationFailed):
            auth.authenticate(request)

    def test_legacy_token_accepted_on_public_schema(self):
        # Legacy tokens without tenant claim should still work on the public schema
        legacy_refresh = RefreshToken.for_user(self.user)
        raw_access = str(legacy_refresh.access_token)

        connection.schema_name = 'public'
        request = self.make_request_with_token(raw_access)
        auth = TenantJWTAuthentication()
        # Should authenticate and return the same user
        user, validated_token = auth.authenticate(request)
        self.assertEqual(user.pk, self.user.pk)
