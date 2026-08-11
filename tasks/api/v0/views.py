from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (CreateAPIView, ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView, GenericAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.shortcuts import get_object_or_404

from .permissions import IsOwner
from .serializers import TaskSerializer
from tasks.models import Category, Task
from accounts.models import Profile

## Write Your Class Base Views Here
class TaskList(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    
    def get(self, request):
        queryset = Task.objects.filter(author=Profile.objects.get(profile_user=self.request.user))
        serializer = TaskSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class TaskDetail(GenericAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = TaskSerializer

    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)
    def put(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)