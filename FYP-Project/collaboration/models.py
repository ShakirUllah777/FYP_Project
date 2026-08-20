from django.db import models
from django.contrib.auth.models import User
from posts.models import Post


class Team(models.Model):
    """A shared workspace created once a post's author starts collaborating
    with one or more students. One Team belongs to exactly one Post."""

    post        = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='team')
    name        = models.CharField(max_length=150, blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams_created')
    members     = models.ManyToManyField(User, related_name='teams', through='TeamMembership')
    created_at  = models.DateTimeField(auto_now_add=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = 'core_team'
        ordering = ['-created_at']

    def __str__(self):
        return self.name or f"Team for {self.post.title}"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.post.title} - Team"
        super().save(*args, **kwargs)


class TeamMembership(models.Model):
    ROLE_CHOICES = [
        ('owner',       'Owner'),
        ('collaborator', 'Collaborator'),
    ]
    team       = models.ForeignKey(Team, on_delete=models.CASCADE)
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    role       = models.CharField(max_length=15, choices=ROLE_CHOICES, default='collaborator')
    joined_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_team_membership'
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.team}"


class TaskItem(models.Model):
    """A single Kanban card inside a Team workspace."""
    STATUS_CHOICES = [
        ('todo',        'To Do'),
        ('in_progress', 'In Progress'),
        ('done',        'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'),
    ]

    team        = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tasks')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_created')
    due_date    = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_task_item'
        ordering = ['status', '-priority', 'due_date']

    def __str__(self):
        return self.title


class Milestone(models.Model):
    """A dated checkpoint for a Post/FYP - proposal, SRS, mid-evaluation,
    final defense, etc. Powers the timeline view."""
    STATUS_CHOICES = [
        ('upcoming',  'Upcoming'),
        ('completed', 'Completed'),
        ('missed',    'Missed'),
    ]

    post        = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='milestones')
    title       = models.CharField(max_length=150)
    description = models.CharField(max_length=300, blank=True)
    due_date    = models.DateField()
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_milestone'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.title} ({self.post.title})"


class ProjectFile(models.Model):
    """A file (proposal doc, code zip, SRS PDF, etc.) shared inside a Team
    workspace so teammates don't have to send it over chat."""
    team        = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file        = models.FileField(upload_to='team_files/%Y/%m/')
    description = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_project_file'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.file.name.split('/')[-1]

    @property
    def filename(self):
        return self.file.name.split('/')[-1]


class MeetingLink(models.Model):
    """A scheduled call for a Team - stores an externally generated
    Google Meet / Zoom link plus the time, rather than embedding full
    WebRTC (out of scope for this project)."""
    team        = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='meetings')
    title       = models.CharField(max_length=150, default='Team Call')
    link        = models.URLField()
    scheduled_for = models.DateTimeField()
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_meeting_link'
        ordering = ['scheduled_for']

    def __str__(self):
        return f"{self.title} @ {self.scheduled_for:%Y-%m-%d %H:%M}"


class Endorsement(models.Model):
    """A formal endorsement of an FYP post by a supervisor/faculty account
    - mirrors the real university FYP-approval workflow."""
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('changes_requested', 'Changes Requested'),
    ]
    post        = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='endorsements')
    supervisor  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='endorsements_given')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks     = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_endorsement'
        unique_together = ('post', 'supervisor')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.post.title} endorsed by {self.supervisor.username} ({self.status})"
