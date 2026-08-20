from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    DEPARTMENT_CHOICES = [('IT', 'IT'), ('CS', 'CS'), ('DS', 'DS'), ('SE', 'SE'), ('EE', 'EE')]
    PROGRAM_CHOICES    = [('BSSE', 'BSSE'), ('BSCS', 'BSCS'), ('BSDS', 'BSDS'), ('BSIT', 'BSIT')]
    SEMESTER_CHOICES   = [(i, f'Semester {i}') for i in range(1, 8)]
    LOOKING_FOR        = [('fyp', 'FYP Partner'), ('paid', 'Paid Task'), ('both', 'Both')]
    AVAILABILITY       = [('5', '<5 hrs/week'), ('5-10', '5–10 hrs/week'), ('10-20', '10–20 hrs/week'), ('20+', '20+ hrs/week')]

    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department   = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES, default='IT', blank=True, null=True)
    program      = models.CharField(max_length=10, choices=PROGRAM_CHOICES, blank=True, null=True)
    semester     = models.IntegerField(choices=SEMESTER_CHOICES, blank=True, null=True)
    photo        = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio          = models.CharField(max_length=200, blank=True)
    github       = models.URLField(blank=True)
    linkedin     = models.URLField(blank=True)
    looking_for  = models.CharField(max_length=10, choices=LOOKING_FOR, blank=True, null=True)
    availability = models.CharField(max_length=10, choices=AVAILABILITY, blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    # --- New: cohort / batch grouping ---
    batch        = models.CharField(max_length=20, blank=True, help_text='e.g. Fall 2022, Spring 2023')

    # --- New: trust & verification ---
    is_verified       = models.BooleanField(default=False, help_text='University email verified')
    id_card            = models.ImageField(upload_to='id_cards/', blank=True, null=True, help_text='Student card photo for senior verification')
    is_id_verified     = models.BooleanField(default=False, help_text='Reviewed and approved by an admin')

    # --- New: role flags ---
    is_supervisor      = models.BooleanField(default=False, help_text='Faculty / supervisor account that can endorse FYP posts')

    # --- New: AI Resume Auto-Fill ---
    resume              = models.FileField(upload_to='resumes/', blank=True, null=True, help_text='Uploaded CV/resume (PDF, DOCX or TXT)')
    resume_updated_at   = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'core_profile'

    def __str__(self):
        return f"{self.user.username}'s Profile"


class EmailVerification(models.Model):
    """One-time token e-mailed to the user to confirm their university
    inbox actually belongs to them."""
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token      = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_email_verification'

    def __str__(self):
        return f"Verification for {self.user.username}"

    @staticmethod
    def generate_token():
        import secrets
        return secrets.token_urlsafe(32)


class SavedSearch(models.Model):
    """A saved Task Feed filter. Lets a student get back to (and later,
    be alerted about) posts matching a skill/type/department combo."""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    label      = models.CharField(max_length=100, blank=True)
    skill      = models.CharField(max_length=100, blank=True)
    post_type  = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_saved_search'
        ordering = ['-created_at']

    def __str__(self):
        return self.label or f"Search by {self.user.username}"

    def matching_posts(self):
        from posts.models import Post
        qs = Post.objects.exclude(author=self.user)
        if self.skill:
            qs = qs.filter(skills_required__name=self.skill)
        if self.post_type:
            qs = qs.filter(post_type=self.post_type)
        return qs


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('programming',  'Programming Languages'),
        ('frameworks',   'Frameworks & Libraries'),
        ('ai_data',      'AI, Data Science & ML'),
        ('databases',    'Databases & Storage'),
        ('devops_cloud', 'DevOps & Cloud'),
        ('mobile',       'Mobile Development'),
        ('web_design',   'Web & UI/UX Design'),
        ('security_qa',  'Cybersecurity & QA'),
        ('others',       'Tools & Other Tech'),
    ]
    name     = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    class Meta:
        db_table = 'core_skill'

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    PROFICIENCY = [
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
    ]
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_skills')
    skill       = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=15, choices=PROFICIENCY)

    class Meta:
        unique_together = ('user', 'skill')
        db_table = 'core_userskill'

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
