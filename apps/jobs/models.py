from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Job(models.Model):
    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full time"
        PART_TIME = "PART_TIME", "Part time"
        INTERNSHIP = "INTERNSHIP", "Internship"
        CONTRACT = "CONTRACT", "Contract"

    title = models.CharField(max_length=180, db_index=True)
    company = models.CharField(max_length=180, db_index=True)
    location = models.CharField(max_length=120, blank=True, db_index=True)
    description = models.TextField()
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=8, default="INR")
    experience_min = models.DecimalField(max_digits=4, decimal_places=1, default=0, validators=[MinValueValidator(0)])
    experience_max = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME)
    required_skills = models.JSONField(default=list, blank=True)
    preferred_skills = models.JSONField(default=list, blank=True)
    source = models.CharField(max_length=60, default="manual", db_index=True)
    external_url = models.URLField(blank=True)
    external_job_id = models.CharField(max_length=120, blank=True, null=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_jobs")

    class Meta:
        ordering = ["-posted_at", "-collected_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("source", "external_job_id"),
                condition=models.Q(external_job_id__isnull=False) & ~models.Q(external_job_id=""),
                name="unique_external_job_per_source",
            ),
            models.CheckConstraint(
                condition=models.Q(salary_max__isnull=True)
                | models.Q(salary_min__isnull=True)
                | models.Q(salary_max__gte=models.F("salary_min")),
                name="job_salary_range_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} at {self.company}"
