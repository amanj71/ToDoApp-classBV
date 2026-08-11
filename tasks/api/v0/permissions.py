from rest_framework import permissions

from accounts.models import Profile

class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to work with it.
    """

    def has_object_permission(self, request, view, obj):
        try:
            profile = Profile.objects.get(profile_user=request.user)
        except Profile.DoesNotExist:
            return False

        return obj.author == profile
    