from django.db import models
from django.contrib.auth.models import User
from accounts.models import Skill


class Post(models.Model):
    TYPE_CHOICES = [('fyp', 'FYP'), ('paid', 'Paid Task')]

    author          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title           = models.CharField(max_length=200)
    post_type       = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description     = models.TextField()
    skills_required = models.ManyToManyField(Skill, blank=True)
    deadline        = models.DateField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'core_post'

    def __str__(self):
        return self.title
