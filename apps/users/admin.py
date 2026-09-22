from django.contrib import admin

from .models import CandidateProfile


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "location", "years_of_experience", "updated_at")
    search_fields = ("full_name", "user__username", "location")

