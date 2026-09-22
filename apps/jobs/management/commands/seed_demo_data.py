from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.applications.models import Application
from apps.jobs.models import Job


class Command(BaseCommand):
    help = "Creates clearly labelled fictional demo jobs and a demo candidate."

    def handle(self, *args, **options):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username="demo_candidate",
            defaults={"email": "demo@example.test", "first_name": "Demo", "last_name": "Candidate"},
        )
        if created:
            user.set_password("DemoPass123!")
            user.save()
        profile = user.candidate_profile
        profile.full_name = "Demo Candidate"
        profile.professional_headline = "Python Django Developer"
        profile.location = "Hyderabad"
        profile.years_of_experience = 0
        profile.skills = ["Python", "Django", "DRF", "SQL", "PostgreSQL", "Docker", "Git"]
        profile.desired_job_titles = ["Python Developer", "Django Developer"]
        profile.preferred_locations = ["Hyderabad", "Remote"]
        profile.minimum_salary = 300000
        profile.maximum_salary = 800000
        profile.save()
        jobs = [
            {
                "title": "Junior Django Developer",
                "company": "Northstar Labs (Demo)",
                "location": "Hyderabad",
                "description": "Fictional demo role building Python and Django REST APIs with PostgreSQL.",
                "required_skills": ["Python", "Django", "DRF", "SQL", "PostgreSQL"],
                "preferred_skills": ["Docker", "Git"],
                "salary_min": 350000,
                "salary_max": 600000,
            },
            {
                "title": "Backend Developer Intern",
                "company": "Orbit Systems (Demo)",
                "location": "Remote",
                "description": "Fictional paid internship for a candidate learning backend APIs, testing, and Docker.",
                "required_skills": ["Python", "SQL", "Git"],
                "preferred_skills": ["Django", "Docker"],
                "salary_min": 240000,
                "salary_max": 360000,
            },
            {
                "title": "Python API Developer",
                "company": "Cedar Stack (Demo)",
                "location": "Hyderabad",
                "description": "Fictional junior backend role maintaining Django services and containerized deployments.",
                "required_skills": ["Python", "Django", "Docker", "AWS"],
                "preferred_skills": ["Celery", "Redis"],
                "salary_min": 450000,
                "salary_max": 750000,
            },
        ]
        created_jobs = []
        for index, data in enumerate(jobs, start=1):
            job, _ = Job.objects.update_or_create(
                source="demo",
                external_job_id=f"demo-{index}",
                defaults={**data, "created_by": user, "employment_type": Job.EmploymentType.FULL_TIME},
            )
            created_jobs.append(job)
        Application.objects.get_or_create(user=user, job=created_jobs[0], defaults={"status": Application.Status.SAVED})
        self.stdout.write(self.style.SUCCESS("Created demo user, profile, three fictional jobs, and one saved application."))
        self.stdout.write("Demo sign-in: username=demo_candidate password=DemoPass123!")
