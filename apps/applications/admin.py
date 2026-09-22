from django.contrib import admin

from .models import Application, CoverLetter


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "user", "status", "follow_up_date", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__username", "job__title", "job__company")


@admin.register(CoverLetter)
class CoverLetterAdmin(admin.ModelAdmin):
    list_display = ("job", "user", "updated_at")
    search_fields = ("user__username", "job__title")
