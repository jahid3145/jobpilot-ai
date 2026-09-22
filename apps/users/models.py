from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class CandidateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate_profile")
    full_name = models.CharField(max_length=150, blank=True)
    professional_headline = models.CharField(max_length=180, blank=True)
    location = models.CharField(max_length=120, blank=True)
    years_of_experience = models.DecimalField(max_digits=4, decimal_places=1, default=0, validators=[MinValueValidator(0)])
    desired_job_titles = models.JSONField(default=list, blank=True)
    preferred_locations = models.JSONField(default=list, blank=True)
    minimum_salary = models.PositiveIntegerField(null=True, blank=True)
    maximum_salary = models.PositiveIntegerField(null=True, blank=True)
    employment_type = models.CharField(max_length=30, blank=True)
    skills = models.JSONField(default=list, blank=True)
    education = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    preferred_technologies = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(maximum_salary__isnull=True)
                | models.Q(minimum_salary__isnull=True)
                | models.Q(maximum_salary__gte=models.F("minimum_salary")),
                name="candidate_salary_range_valid",
            )
        ]

    def __str__(self) -> str:
        return self.full_name or self.user.get_username()

