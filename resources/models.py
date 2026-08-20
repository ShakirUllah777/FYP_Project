from django.db import models


class Resource(models.Model):
    """A downloadable FYP resource - proposal template, SRS template,
    defense checklist, etc. Populated by admins via the Django admin panel
    or the seed_resources management command."""

    CATEGORY_CHOICES = [
        ('proposal',  'Proposal Template'),
        ('srs',       'SRS / Requirements Template'),
        ('report',    'Final Report Template'),
        ('checklist', 'Defense / Evaluation Checklist'),
        ('guideline', 'General Guideline'),
        ('other',     'Other'),
    ]

    title       = models.CharField(max_length=200)
    category    = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    file        = models.FileField(upload_to='resources/', blank=True, null=True)
    external_link = models.URLField(blank=True)
    department  = models.CharField(max_length=10, blank=True, help_text='Leave blank to show to all departments')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_resource'
        ordering = ['category', 'title']

    def __str__(self):
        return self.title
