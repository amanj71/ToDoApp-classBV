from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from . import views

urlpatterns = [
    #register new user
    path('register-new-user/', views.RegisterNewUserAPI.as_view(), name='register-new-user'),
    #activation link & resend it
    path('active/<str:token>', views.ActiveUserAPI.as_view(), name='active-user-api'),
    path('resend-activation-link/', views.ResendActivationLinkAPI.as_view(),
         name='resend-activation-link'),
    #login and logout user with jwt tiken
    path('login/', views.LoginUserJwtAPI.as_view(), name='login-user'),
    path('logout/', TokenBlacklistView.as_view(), name='logout-user'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh-token'),
    #change and reset password API
    path('change-user-password/', views.UserChangePasswordAPI.as_view(), name='change-user-password'),
    path('reset-user-password/', views.UserResetPasswordAPI.as_view(), name='reset-user-password'),
    path('change-user-reseted-password/<str:token>', views.UserChangeResettedPasswordAPI.as_view(),
         name='change-user-reseted-password'),
]