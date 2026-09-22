from django.contrib import admin

from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_primary", "uploaded_at", "updated_at")
    list_filter = ("is_primary",)
    search_fields = ("title", "user__username")
    readonly_fields = ("extracted_text", "parsed_data", "uploaded_at", "updated_at")
