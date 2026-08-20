from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from posts.models import Post


class Review(models.Model):
    """A rating + comment left by one student about another after working
    together on a Post (FYP team or paid task). Mirrors marketplace
    platforms like Upwork/Fiverr so trust can be built on the platform."""

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    reviewer      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    post          = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    rating        = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment       = models.TextField(max_length=1000, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_review'
        ordering = ['-created_at']
        unique_together = ('reviewer', 'reviewed_user', 'post')

    def __str__(self):
        return f"{self.reviewer.username} -> {self.reviewed_user.username} ({self.rating}star)"

    @property
    def stars_range(self):
        return range(self.rating)

    @staticmethod
    def average_for(user):
        agg = Review.objects.filter(reviewed_user=user).aggregate(avg=Avg('rating'), count=Count('id'))
        return {
            'average': round(agg['avg'], 1) if agg['avg'] else None,
            'count': agg['count'] or 0,
        }


class Report(models.Model):
    """User-submitted report used for the moderation queue. Can flag a
    user and, optionally, a specific post."""

    REASON_CHOICES = [
        ('spam',         'Spam or misleading'),
        ('harassment',   'Harassment or abusive behaviour'),
        ('scam',         'Scam / non-payment for a paid task'),
        ('fake_profile', 'Fake profile or impersonation'),
        ('inappropriate', 'Inappropriate content'),
        ('other',        'Other'),
    ]
    STATUS_CHOICES = [
        ('open',      'Open'),
        ('reviewing', 'Under Review'),
        ('resolved',  'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    reporter      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_filed')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_against')
    post          = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    reason        = models.CharField(max_length=20, choices=REASON_CHOICES)
    details       = models.TextField(max_length=1000, blank=True)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    admin_notes   = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    resolved_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_report'
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.pk}: {self.reported_user.username} ({self.get_reason_display()})"
