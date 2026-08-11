from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

## Create Your serializers here
class RegisterNewUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError('Passwords should match each other!')
        try:
            validate_password(attrs.get('password'))
        except exceptions.ValidationError as errors:
            raise serializers.ValidationError({'password': list(errors.messages)})
        return super().validate(attrs)
    
    def create(self, validated_data):
        validated_data['email'] = validated_data['username'] + '@example.com'
        validated_data.pop('confirm_password', None)
        return User.objects.create_user(**validated_data)

class ResendActivationLinkSerializer(serializers.Serializer):
    email = serializers.EmailField()

class UserTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # include tenant information in the token so tokens cannot be reused across tenants
        token = super().get_token(user)
        try:
            from django.db import connection
            tenant_schema = getattr(connection, 'schema_name', 'public')
        except Exception:
            tenant_schema = 'public'
        token['tenant'] = tenant_schema
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_staff:
            raise serializers.ValidationError("Please activate your account first.")
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"detail": "old password doesn't correct!"})
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value, user=self.context["request"].user)
        except exceptions.ValidationError as errors:
            raise serializers.ValidationError({"password": list(errors.messages)})
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password must be different from the old password."}
            )
        return attrs

class ChangeResettedPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        try:
            validate_password(attrs['password'])
        except exceptions.ValidationError as errors:
            raise serializers.ValidationError({"password": list(errors.messages)})

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})

        return attrs
