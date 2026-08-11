from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.shortcuts import get_object_or_404

from .permissions import IsOwner
from .serializers import TaskSerializer
from tasks.models import Task
from accounts.models import Profile


def _get_current_profile(user):
    return Profile.objects.get(profile_user=user)

## Write Your Class Base Views Here
class TaskList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        profile = _get_current_profile(request.user)
        queryset = Task.objects.filter(author=profile)
        serializer = TaskSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class TaskDetail(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk, author=_get_current_profile(request.user))
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        task = get_object_or_404(Task, id=pk, author=_get_current_profile(request.user))
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        task = get_object_or_404(Task, id=pk, author=_get_current_profile(request.user))
        self.check_object_permissions(request, task)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)