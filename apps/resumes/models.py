from django.conf import settings
from django.db import models


class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to="resumes/%Y/%m/", blank=True)
    extracted_text = models.TextField(blank=True)
    parsed_data = models.JSONField(default=dict, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ("-is_primary", "-updated_at")
        constraints = [
            models.UniqueConstraint(
                fields=("user",),
                condition=models.Q(is_primary=True),
                name="one_primary_resume_per_user",
            )
        ]

    def __str__(self) -> str:
        return self.title

