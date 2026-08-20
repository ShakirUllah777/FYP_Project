from django.db import models
from django.contrib.auth.models import User
from accounts.models import Skill


class Post(models.Model):
    TYPE_CHOICES = [('fyp', 'FYP'), ('paid', 'Paid Task')]
    COMPLEXITY_CHOICES = [
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
    ]

    author          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title           = models.CharField(max_length=200)
    post_type       = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description     = models.TextField()
    skills_required = models.ManyToManyField(Skill, blank=True)
    deadline        = models.DateField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    # --- New: marks a post/task as finished, unlocking reviews ---
    is_completed    = models.BooleanField(default=False)

    # --- New: AI project-scope estimate (feature: AI scope estimator) ---
    estimated_complexity = models.CharField(max_length=15, choices=COMPLEXITY_CHOICES, blank=True)
    estimated_timeline    = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'core_post'

    def __str__(self):
        return self.title


class Bookmark(models.Model):
    """Lets a user save a post to revisit later (feature: Saved Posts / Bookmarks)."""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user.username} \u2192 {self.post.title}'
