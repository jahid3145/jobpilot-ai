import os
import tempfile
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.applications.models import Application
from apps.applications.services import CoverLetterService
from apps.jobs.models import Job
from apps.jobs.services import JobIngestionService, JobMatchingService
from apps.resumes.models import Resume
from apps.resumes.services import ResumeParserService
from apps.ai_agent.tools import (
    search_jobs_tool,
    calculate_job_match_tool,
    generate_cover_letter_tool,
    list_applications_tool,
)

User = get_user_model()


class ExtendedServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fresher_dev", password="safe-password-123")
        self.profile = self.user.candidate_profile
        self.profile.full_name = "Fresher Developer"
        self.profile.location = "Hyderabad"
        self.profile.preferred_locations = ["Hyderabad"]
        self.profile.skills = ["Python", "Django", "DRF", "SQL", "Docker"]
        self.profile.years_experience = 0
        self.profile.minimum_salary = 300000
        self.profile.maximum_salary = 800000
        self.profile.save()

        self.job = Job.objects.create(
            title="Python Django Developer",
            company="Tech Corp",
            location="Hyderabad",
            description="Looking for Python, Django, DRF, SQL, and Docker skills.",
            required_skills=["Python", "Django", "DRF", "SQL"],
            preferred_skills=["Docker", "AWS"],
            salary_min=400000,
            salary_max=700000,
            experience_min=0,
            experience_max=2,
        )

    def test_resume_parser_extracts_skills(self):
        sample_text = "Experienced in Python, Django, REST API development, SQL, and Git."
        parsed = ResumeParserService.parse_text(sample_text)

        self.assertIn("python", parsed["skills"])
        self.assertIn("django", parsed["skills"])
        self.assertIn("sql", parsed["skills"])

    def test_job_ingestion_service_creates_job_without_duplicates(self):
        raw_job = {
            "title": "Backend Engineer",
            "company": "Fictional Corp",
            "location": "Remote",
            "description": "Django REST API backend engineer.",
            "required_skills": ["Python", "Django"],
            "source": "mock",
            "external_job_id": "MOCK-1001",
        }
        job1 = JobIngestionService.create_or_update_job(raw_job)
        job2 = JobIngestionService.create_or_update_job(raw_job)

        self.assertEqual(job1.id, job2.id)
        self.assertEqual(Job.objects.filter(external_job_id="MOCK-1001").count(), 1)

    def test_job_matching_service_breakdown(self):
        self.job.required_skills = ["Python", "Django", "DRF", "SQL", "AWS"]
        self.job.save()

        matching_service = JobMatchingService(self.profile)
        result = matching_service.calculate_match(self.job)

        self.assertGreaterEqual(result["overall_match"], 70)
        self.assertIn("python", result["matching_skills"])
        self.assertIn("aws", result["missing_skills"])



    def test_agent_tools_execution(self):
        # 1. Search jobs tool
        search_res = search_jobs_tool(self.user, role="Python", location="Hyderabad")
        self.assertTrue(search_res["success"])
        self.assertGreaterEqual(search_res["data"]["total"], 1)

        # 2. Calculate match tool
        match_res = calculate_job_match_tool(self.user, job_id=self.job.id)
        self.assertTrue(match_res["success"])
        self.assertIn("overall_match", match_res["data"])

        # 3. Generate cover letter tool
        letter_res = generate_cover_letter_tool(self.user, job_id=self.job.id)
        self.assertTrue(letter_res["success"])
        self.assertIn("Fresher Developer", letter_res["data"]["cover_letter"])

        # 4. List applications tool
        Application.objects.create(user=self.user, job=self.job, status="APPLIED")
        apps_res = list_applications_tool(self.user)
        self.assertTrue(apps_res["success"])
        self.assertEqual(len(apps_res["data"]["applications"]), 1)

    def test_applications_api_flow(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        # Create application
        resp = client.post("/api/applications/", {"job": self.job.id, "status": "SAVED"}, format="json")
        self.assertEqual(resp.status_code, 201)

        app_id = resp.data["id"]

        # Update application status
        patch_resp = client.patch(f"/api/applications/{app_id}/", {"status": "INTERVIEW"}, format="json")
        self.assertEqual(patch_resp.status_code, 200)
        self.assertEqual(patch_resp.data["status"], "INTERVIEW")
