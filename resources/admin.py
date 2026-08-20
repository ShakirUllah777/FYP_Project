from django.contrib import admin
from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'department', 'created_at')
    list_filter = ('category', 'department')
    search_fields = ('title', 'description')
