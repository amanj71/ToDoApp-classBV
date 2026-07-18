from django.db import models
from accounts.models import Profile

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICE = {
        "F": "Future",
        "P": "Pending",
        "C": "Completed",
    }
    TASK_IMPORTANCE_CHOICE = {
        "H": "High",
        "M": "Medium",
        "L": "Low",
    }
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=1, choices=STATUS_CHOICE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    importance = models.CharField(max_length=1, choices=TASK_IMPORTANCE_CHOICE)
    
    created_date = models.DateTimeField(auto_now_add=True)
    edited_date = models.DateTimeField(auto_now=True)
    completed_date = models.DateTimeField(blank=True, null=True)