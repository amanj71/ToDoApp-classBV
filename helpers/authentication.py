from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.db import connection

class TenantJWTAuthentication(JWTAuthentication):
    """Extend SimpleJWT's JWTAuthentication to enforce that the token's tenant
    claim matches the currently active DB schema (set by TenantSchemaMiddleware).

    Behavior:
    - If token contains a 'tenant' claim, it must equal connection.schema_name.
    - If token lacks 'tenant' claim, reject access when connection.schema_name != 'public'.
      (This makes older tokens without tenant-binding invalid for non-public tenants.)
    """

    def authenticate(self, request):
        # Use parent to extract and validate token; but perform tenant check first.
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = None
        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception as e:
            # Let parent raise appropriate exceptions for invalid tokens
            raise

        token_tenant = validated_token.get('tenant', None)
        current_schema = getattr(connection, 'schema_name', 'public')

        # If token has tenant claim, it must match current schema
        if token_tenant is not None:
            if str(token_tenant) != str(current_schema):
                raise AuthenticationFailed('Token tenant does not match the request tenant.')
        else:
            # No tenant in token: treat as legacy token and only allow on public schema
            if current_schema != 'public':
                raise AuthenticationFailed('Token not bound to a tenant; access denied for this tenant.')

        user = self.get_user(validated_token)
        return (user, validated_token)
