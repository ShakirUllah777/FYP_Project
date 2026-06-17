from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    DEPARTMENT_CHOICES = [('IT','IT'),('CS','CS'),('DS','DS'),('SE','SE'),('EE','EE')]
    PROGRAM_CHOICES    = [('BSSE','BSSE'),('BSCS','BSCS'),('BSDS','BSDS'),('BSIT','BSIT')]
    SEMESTER_CHOICES   = [(i, f'Semester {i}') for i in range(1, 8)]
    LOOKING_FOR        = [('fyp','FYP Partner'),('paid','Paid Task'),('both','Both')]
    AVAILABILITY       = [('5','<5 hrs/week'),('5-10','5–10 hrs/week'),('10-20','10–20 hrs/week'),('20+','20+ hrs/week')]

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

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}"


class Post(models.Model):
    TYPE_CHOICES = [('fyp','FYP'),('paid','Paid Task')]

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

    def __str__(self):
        return self.title


class Message(models.Model):
    sender   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content  = models.TextField()
    sent_at  = models.DateTimeField(auto_now_add=True)
    is_read  = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}"


class Block(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)