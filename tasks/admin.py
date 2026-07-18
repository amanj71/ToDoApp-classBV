from django.contrib import admin
from .models import Category, Task

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'creator']

class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'status', 'importance', 'category']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Task, TaskAdmin)