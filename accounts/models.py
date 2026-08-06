from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    class Meta:
        db_table = 'core_profile'

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('programming', 'Programming Languages'),
        ('frameworks',  'Frameworks'),
        ('ai_data',     'AI / Data'),
        ('databases',   'Databases'),
        ('others',      'Others'),
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
