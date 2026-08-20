from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

from accounts.models import Skill


class Community(models.Model):
    """A topic-based community hub (e.g. Web Development, Cybersecurity,
    Python Developers). Students auto-qualify as members based on skills
    they've added to their profile, and can also join manually to show
    interest even before they've picked up the matching skills."""

    name           = models.CharField(max_length=100, unique=True)
    slug           = models.SlugField(max_length=110, unique=True, blank=True)
    description    = models.CharField(max_length=220)
    icon           = models.CharField(max_length=40, default='bi-people-fill',
                                       help_text='Bootstrap icon class, e.g. bi-code-slash')
    color          = models.CharField(max_length=7, default='#1B6FFF', help_text='Hex color for the community badge/icon')
    related_skills = models.ManyToManyField(Skill, blank=True, related_name='communities',
                                             help_text='Skills that auto-qualify a student for this community')
    order          = models.PositiveIntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_community'
        ordering = ['order', 'name']
        verbose_name_plural = 'Communities'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def member_count(self):
        return self.members.count()


class CommunityMembership(models.Model):
    """Explicit 'Join' by a user. Skill-based members are computed
    dynamically (see the community_detail view), while this table tracks
    who actively opted in."""
    community  = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='members')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communities')
    joined_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_membership'
        unique_together = ('community', 'user')
        ordering = ['-joined_at']

    def __str__(self):
        return f'{self.user.username} in {self.community.name}'
