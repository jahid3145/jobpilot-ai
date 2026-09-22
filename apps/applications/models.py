from django.conf import settings
from django.db import models

from apps.jobs.models import Job


class Application(models.Model):
    class Status(models.TextChoices):
        SAVED = "SAVED", "Saved"
        APPLIED = "APPLIED", "Applied"
        INTERVIEW = "INTERVIEW", "Interview"
        REJECTED = "REJECTED", "Rejected"
        SELECTED = "SELECTED", "Selected"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SAVED, db_index=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        constraints = [models.UniqueConstraint(fields=("user", "job"), name="one_application_per_user_job")]

    def __str__(self) -> str:
        return f"{self.user} — {self.job}"


class CoverLetter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cover_letters")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="cover_letters")
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True, blank=True, related_name="cover_letters")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

