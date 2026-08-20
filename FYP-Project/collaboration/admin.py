from django.contrib import admin
from .models import Team, TeamMembership, TaskItem, Milestone, ProjectFile, MeetingLink, Endorsement


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'created_by', 'created_at', 'is_active')
    inlines = [TeamMembershipInline]


@admin.register(TaskItem)
class TaskItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'team', 'status', 'priority', 'assigned_to', 'due_date')
    list_filter = ('status', 'priority')


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'post', 'due_date', 'status')
    list_filter = ('status',)


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('filename', 'team', 'uploaded_by', 'uploaded_at')


@admin.register(MeetingLink)
class MeetingLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'team', 'scheduled_for', 'created_by')


@admin.register(Endorsement)
class EndorsementAdmin(admin.ModelAdmin):
    list_display = ('post', 'supervisor', 'status', 'updated_at')
    list_filter = ('status',)
