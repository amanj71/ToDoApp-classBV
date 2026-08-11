from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class TenantAwareJWTAuthentication(JWTAuthentication):
    """JWT authentication that locks the token to the authenticated user's identity.

    This prevents a token issued for a user in one tenant context from being reused
    in another tenant when the same user ID exists in a different schema.
    """

    TENANT_HEADER = 'HTTP_X_TENANT_ID'

    def authenticate(self, request):
        raw_token = self.get_raw_token(self.get_header(request))
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        self.check_token_tenant(validated_token, request)
        return user, validated_token

    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        token_username = validated_token.get('username')
        token_email = validated_token.get('email')

        if token_username is None or token_email is None:
            raise AuthenticationFailed(_("Invalid token payload."))

        if user.username != token_username or user.email != token_email:
            raise AuthenticationFailed(
                _("Token user information does not match the authenticated user."))

        return user

    def check_token_tenant(self, validated_token, request):
        token_tenant = validated_token.get('tenant')
        if not token_tenant:
            return

        request_tenant = self.get_request_tenant(request)
        if request_tenant != token_tenant:
            raise AuthenticationFailed(
                _("Token tenant does not match the current request tenant."))

    def get_request_tenant(self, request):
        tenant_from_header = request.META.get(self.TENANT_HEADER)
        if tenant_from_header:
            return tenant_from_header
        host = request.get_host()
        return host.split(':')[0] if host else None
