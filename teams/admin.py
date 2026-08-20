from django.contrib import admin
from .models import Team, TaskItem


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['post', 'member_count', 'created_at']
    search_fields = ['post__title']
    filter_horizontal = ['members']


@admin.register(TaskItem)
class TaskItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'team', 'status', 'priority', 'assignee', 'due_date']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'team__post__title']
