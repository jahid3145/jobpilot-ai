from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "employment_type", "is_active", "collected_at")
    list_filter = ("employment_type", "is_active", "source")
    search_fields = ("title", "company", "location")
