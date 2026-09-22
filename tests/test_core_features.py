from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APIClient

from apps.applications.models import Application
from apps.applications.services import CoverLetterService
from apps.jobs.models import Job
from apps.jobs.services import JobMatchingService

User = get_user_model()


class JobPilotCoreTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="candidate", password="safe-password-123")
        self.profile = self.user.candidate_profile
        self.profile.full_name = "Candidate One"
        self.profile.location = "Hyderabad"
        self.profile.preferred_locations = ["Hyderabad"]
        self.profile.skills = ["Python", "Django", "SQL"]
        self.profile.minimum_salary = 300000
        self.profile.save()
        self.job = Job.objects.create(
            title="Django Developer",
            company="Fictional Labs",
            location="Hyderabad",
            description="Build web APIs.",
            required_skills=["Python", "Django", "SQL"],
            salary_min=300000,
            salary_max=500000,
        )

    def test_matching_returns_transparent_score_and_missing_skills(self):
        match = JobMatchingService(self.profile).calculate_match(self.job)

        self.assertEqual(match["overall_match"], 100)
        self.assertEqual(match["missing_skills"], [])
        self.assertEqual(match["breakdown"]["skills"], 100)

    def test_duplicate_applications_are_prevented_by_database(self):
        Application.objects.create(user=self.user, job=self.job)

        with self.assertRaises(IntegrityError):
            Application.objects.create(user=self.user, job=self.job)

    def test_cover_letter_only_uses_saved_candidate_facts(self):
        letter = CoverLetterService().generate(self.profile, None, self.job)

        self.assertIn("Candidate One", letter)
        self.assertIn("Python", letter)
        self.assertNotIn("ten years", letter.lower())

    def test_dashboard_requires_login_then_renders_for_candidate(self):
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get("/dashboard/")
        self.assertContains(response, "Best matches")


class ApiTests(TestCase):
    def test_register_endpoint_creates_user_profile(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "new_user", "email": "new@example.test", "password": "safe-password-123"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.get(username="new_user").candidate_profile)

    def test_agent_search_only_returns_controlled_tool_result(self):
        user = User.objects.create_user(username="agent_user", password="safe-password-123")
        Job.objects.create(
            title="Python Developer",
            company="Fictional Labs",
            location="Hyderabad",
            description="Build APIs.",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/agent/chat/", {"message": "Find Python jobs in Hyderabad"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["tool"], "search_jobs")
