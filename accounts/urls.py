from django.urls import path, include

urlpatterns = [
    path('api/', include('accounts.api.v0.urls')),
]