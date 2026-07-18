from django import forms
from .models import Category, Task
from accounts.models import Profile

# Create your forms here
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'status', 'category', 'importance']
        exclude = ['author',]

    def __init__(self, *args, **kwargs):
        """
        redefine __init__ constructor to get category list created by the logged in user
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            profile = Profile.objects.get(profile_user=user)
            self.fields['category'].queryset = Category.objects.filter(creator=profile)