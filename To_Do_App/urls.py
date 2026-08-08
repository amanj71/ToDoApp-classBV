"""
URL configuration for To_Do_App project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.urls import path, include

## Implement API Documentation structure here
schema_view = get_schema_view(
   openapi.Info(
      title="ToDoApp-CBV API", # you can assign a name to your documentation api
      default_version='v0',   # assign a version you want
      description="Practice Class Base View Django",  # write any description for your api doc
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

## paths
urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('django.contrib.auth.urls')),
    # API Documentation URLs
    path('swagger.<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'), #Specific
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('tasks/', include('tasks.urls')),
]
