from django.contrib import admin
from .models import Community, CommunityMembership


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'order')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('related_skills',)


@admin.register(CommunityMembership)
class CommunityMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'community', 'joined_at')
    list_filter = ('community',)
