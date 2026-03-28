from django.contrib import admin
from .models import Profile, Skill, UserSkill, Post, Message

admin.site.register(Profile)
admin.site.register(Skill)
admin.site.register(UserSkill)
admin.site.register(Post)
admin.site.register(Message)