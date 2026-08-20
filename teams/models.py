from django.db import models
from django.contrib.auth.models import User
from posts.models import Post


class Team(models.Model):
    post       = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='team')
    members    = models.ManyToManyField(User, related_name='teams', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Team for: {self.post.title}"

    def member_count(self):
        return self.members.count()


class TaskItem(models.Model):
    STATUS_CHOICES = [
        ('todo',        'To Do'),
        ('in_progress', 'In Progress'),
        ('done',        'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]

    team       = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='task_items')
    title      = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority   = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assignee   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    due_date   = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', '-created_at']

    def __str__(self):
        return self.title

    def priority_color(self):
        return {'low': 'success', 'medium': 'warning', 'high': 'danger'}[self.priority]

    def status_color(self):
        return {'todo': 'secondary', 'in_progress': 'primary', 'done': 'success'}[self.status]
