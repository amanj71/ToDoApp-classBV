from django.views.generic import TemplateView ,ListView, DetailView, FormView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Task, VisitPages
from django.contrib import messages

from accounts.models import Profile
from .forms import TaskForm


# Create your views here.
class ImplementationTemplate(TemplateView):
    pass


class TaskList(LoginRequiredMixin,ListView, FormView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    form_class = TaskForm
    success_url = '/tasks/'

    def get(self, request):
        visit_obj = VisitPages.objects.create(path='/tasks/', user=request.user)
        return super().get(request)

    def get_queryset(self):
        return self.model.objects.filter(author=Profile.objects.get(profile_user=self.request.user))
    
    def get_form_kwargs(self):
        """
        adds user object to the data which are going to pass to the modelform, without this we
        can not access user instance in __init__ method inside form-model class.  
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """ 
        rewrite form_valid because of pass author field to the model's data automatically.
        """
        form.instance.author = Profile.objects.get(profile_user=self.request.user)
        form.save()
        messages.success(self.request, 'New Task Added')
        return super().form_valid(form)
    
class TaskDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    def get(self, request, pk):
        visit_obj = VisitPages.objects.create(path='/id_task/', user=request.user)
        return super().get(request, pk)

    def test_func(self):
        """
        this method ensures that every users just can edit thier own tasks, even if you passed
        another user's task id by url, this method block others user to get achive the task.
        IMPORTANT: this method needs UserPassesTestMixin class has been registered, which Deny
        a request with a permission error if the test_func() method returns False.
        """
        task = self.get_object()
        return task.author == Profile.objects.get(profile_user=self.request.user)

class TaskEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    template_name = 'tasks/task_edit.html'
    success_url = '/tasks/'
    form_class = TaskForm
    
    def test_func(self):
        """
        this method ensures that every users just can edit thier own tasks, even if you passed
        another user's task id by url, this method block others user to get achive the task.
        IMPORTANT: this method needs UserPassesTestMixin class has been registered, which Deny
        a request with a permission error if the test_func() method returns False.
        """
        task = self.get_object()
        return task.author == Profile.objects.get(profile_user=self.request.user) 
    
    def get_form_kwargs(self):
        """
        adds user object to the data which are going to pass to the modelform, without this we
        can not access user instance in __init__ method inside form-model class.  
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs  
    
    def form_valid(self, form):
        """ 
        rewrite form_valid because of pass author field to the model's data automatically.
        """
        form.instance.author = Profile.objects.get(profile_user=self.request.user)
        form.save()
        messages.success(self.request, 'Task Editted Correctly')
        return super().form_valid(form)

class TaskDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    success_url = '/tasks/'
    
    def test_func(self):
        """
        this method ensures that every users just can edit thier own tasks, even if you passed
        another user's task id by url, this method block others user to get achive the task.
        IMPORTANT: this method needs UserPassesTestMixin class has been registered, which Deny
        a request with a permission error if the test_func() method returns False.
        """
        task = self.get_object()
        return task.author == Profile.objects.get(profile_user=self.request.user)
