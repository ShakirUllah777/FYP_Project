from django.contrib import admin
from .models import Profile, Skill, UserSkill, Post, Message, Block

admin.site.register(Profile)
admin.site.register(Skill)
admin.site.register(UserSkill)
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(Block)