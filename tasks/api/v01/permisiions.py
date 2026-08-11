from rest_framework.permissions import BasePermission
from tasks.models import Category, Task
from accounts.models import Profile

## Create your permission clases here
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            profile = Profile.objects.get(profile_user=request.user)
        except Profile.DoesNotExist:
            return False
        return obj.author == profile