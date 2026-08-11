from django.views.generic import ListView, FormView
from django.contrib import messages

from accounts.models import Profile
from tasks.models import Task, VisitPages
from tasks.forms import TaskForm


class Home(ListView, FormView):
    model = Task
    template_name = 'base.html'
    context_object_name = 'tasks'

    form_class = TaskForm
    success_url = ''

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        visit_obj = VisitPages.objects.create(path='home', user=user)
        return super().get(request)
