from django.urls import path
from .views import ImplementationTemplate ,TaskList, TaskDetail, TaskEdit, TaskDelete

app_name = 'tasks'

urlpatterns = [
    path('implementation/', ImplementationTemplate.as_view(), name='for-implementation'),
    path('', TaskList.as_view(), name='task-list'),
    path('<int:pk>', TaskDetail.as_view(), name='task-detail'),
    path('<int:pk>/edit', TaskEdit.as_view(), name='task-edit'),
    path('<int:pk>/delete', TaskDelete.as_view(), name='task-delete'),
]
