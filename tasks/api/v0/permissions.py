from rest_framework import permissions

from accounts.models import Profile

class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to work with it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == Profile.objects.get(profile_user=request.user)
    