from django.contrib import admin
from .models import Review, Report


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewed_user', 'post', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__username', 'reviewed_user__username')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'reported_user', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason')
    search_fields = ('reporter__username', 'reported_user__username')
