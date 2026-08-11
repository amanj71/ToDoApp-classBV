from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory
from accounts.api.v0.authentication import TenantAwareJWTAuthentication


class TenantAwareJWTAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tenant_user',
            email='tenant_user@example.com',
            password='secret123',
        )
        self.factory = APIRequestFactory()

    def test_authentication_rejects_mismatched_token_claims(self):
        refresh_token = RefreshToken.for_user(self.user)
        access_token = refresh_token.access_token
        access_token['username'] = 'other_user'
        access_token['email'] = self.user.email

        request = self.factory.get('/')
        auth = TenantAwareJWTAuthentication()

        validated_token = auth.get_validated_token(str(access_token))
        with self.assertRaises(AuthenticationFailed):
            auth.get_user(validated_token)
