from django.contrib import admin
from .models import Profile, Skill, UserSkill, EmailVerification, SavedSearch


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'program', 'semester', 'batch', 'is_verified', 'is_id_verified', 'is_supervisor')
    list_filter = ('department', 'program', 'is_verified', 'is_id_verified', 'is_supervisor')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'batch')
    actions = ['approve_id_verification']

    @admin.action(description='Approve selected ID verifications')
    def approve_id_verification(self, request, queryset):
        updated = queryset.update(is_id_verified=True)
        self.message_user(request, f'{updated} profile(s) marked as ID-verified.')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Skill)
admin.site.register(UserSkill)
admin.site.register(EmailVerification)
admin.site.register(SavedSearch)
