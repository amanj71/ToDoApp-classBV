from rest_framework.permissions import BasePermission
from tasks.models import Category, Task
from accounts.models import Profile

## Create your permission clases here
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == Profile.objects.get(profile_user=request.user)