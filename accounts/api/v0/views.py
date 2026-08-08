from rest_framework.response import Response
from rest_framework.generics import (CreateAPIView, ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView, GenericAPIView)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

import jwt
from jwt import exceptions as jwtexceptions

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (RegisterNewUserSerializer, ResendActivationLinkSerializer,
                          UserTokenObtainSerializer, ChangePasswordSerializer,
                          ChangeResettedPasswordSerializer)
from ...utils import (ActivationToken, ResetPasswordToken, create_activation_token,
                      create_reset_password_token)

## Create your views here
class RegisterNewUserAPI(CreateAPIView):
    serializer_class = RegisterNewUserSerializer

    def post(self, request, *args, **kwargs):
        #create user 
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_user = serializer.save()

        # create verification link
        activation_token = create_activation_token(created_user)
        activation_token_url = f"localhost:8000/accounts/api/active/?token={activation_token}"
        activation_token_url = activation_token

        # send a verification email
        context = {
            'username': serializer.validated_data['username'],
            'site_name': 'Class Base View Todolist',
            'activation_link': activation_token_url,
        }

        text_content = render_to_string("emails/activation_link.txt", context,)
        html_content = render_to_string("emails/activation_link.html", context)

        msg = EmailMultiAlternatives(
            subject="Active Link",
            body=text_content,
            from_email="todo@classbassviewapp.com",
            to=[serializer.validated_data['username']],
            headers={"List-Unsubscribe": "<mailto:unsub@example.com>"},
        )

        msg.attach_alternative(html_content, "text/html")
        msg.send()

        messages = {
            'message': 'User Created Successfully',
            "detail": "activation link sent to your email."
        }

        return Response(messages, status=status.HTTP_201_CREATED)

class ActiveUserAPI(APIView):
    def get(self, request, token):
        try:
            decode_token = ActivationToken(token)
            if decode_token["purpose"] != "activation":
                raise TokenError("Invalid token")
            user_id = decode_token['user_id']
        except Exception:
            return Response({"detail": "Invalid or expired token."},
                            status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, id=user_id)
        if user.is_staff:
            return Response({'details': 'Your account is ALREADY known as staff!'})
        user.is_staff = True
        user.save()
        return Response({'details': 'Your account is verified & activated'})

class ResendActivationLinkAPI(GenericAPIView):
    serializer_class = ResendActivationLinkSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data or None)
        serializer.is_valid(raise_exception=True)
        user_email = serializer.validated_data['email']
        
        text = 'If account exists and is not active yet, new link has been sent!'
        generic = Response({'detail': text}, status=status.HTTP_200_OK)
        try:
            user = User.objects.get(email=user_email)
            token = create_activation_token(user)
        except:
            return generic

        if user.is_staff == True:
            return generic
        
        context = {
            'email': user_email,
            'site_name': 'Class Base View Todolist',
            'activation_link': token,
        }
        text_content = render_to_string("emails/activation_link.txt", context,)
        html_content = render_to_string("emails/activation_link.html", context)

        msg = EmailMultiAlternatives(
            subject="Resend Active Link",
            body=text_content,
            from_email="todo@classbassviewapp.com",
            to=[serializer.validated_data['email']],
            headers={"List-Unsubscribe": "<mailto:unsub@example.com>"},
        )

        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return generic

class LoginUserJwtAPI(TokenObtainPairView):
    serializer_class = UserTokenObtainSerializer

class UserChangePasswordAPI(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request):
        print("Request data:", request.data)
        user = request.user
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=["password"])
        return Response({"detail": "Password changed successfully."},status=status.HTTP_200_OK)

class UserResetPasswordAPI(GenericAPIView):
    serializer_class = ResendActivationLinkSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        text = 'If account exists and be activated, reset pass link has been sent!'
        generic = Response({'detail': text}, status=status.HTTP_200_OK)
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            token = create_reset_password_token(user)
        except user.DoesNotExist:
            return generic

        if not user.is_staff :
            return generic
        
        context = {
            'email': user.email,
            'site_name': 'Class Base View Todolist',
            'activation_link': token,
        }
        text_content = render_to_string("emails/activation_link.txt", context,)
        html_content = render_to_string("emails/activation_link.html", context)

        msg = EmailMultiAlternatives(
            subject="Reset Password Link",
            body=text_content,
            from_email="todo@classbassviewapp.com",
            to=[user.email],
            headers={"List-Unsubscribe": "<mailto:unsub@example.com>"},
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return generic

class UserChangeResettedPasswordAPI(GenericAPIView):
    serializer_class = ChangeResettedPasswordSerializer

    def put(self, request, token):
        try:
            decode_token = ResetPasswordToken(token)
            if decode_token["purpose"] != "reset-password":
                raise TokenError("Invalid token")
            user_id = decode_token['user_id']
        except Exception:
            return Response({"detail": "Invalid or expired token."},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=user_id)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data['password'])
        user.save(update_fields=["password"])

        return Response({"detail": "new password has been set for your account!"})

        