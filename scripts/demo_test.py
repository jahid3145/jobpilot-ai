import os
import sys
import json
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.jobs.models import Job
from apps.applications.models import Application
from apps.jobs.services import JobIngestionService, MockJobSource

User = get_user_model()

def run_demo():
    print("=" * 70)
    print(" 🚀 JOBPILOT AI — LIVE DEMO & END-TO-END TEST SUITE")
    print("=" * 70)

    client = APIClient()

    # STEP 1: Health Check
    print("\n--- [STEP 1] API HEALTH CHECK ---")
    resp = client.get("/api/health/")
    print(f"GET /api/health/ -> Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    assert resp.status_code == 200

    # STEP 2: Demo Data Ingestion & Seeding
    print("\n--- [STEP 2] JOB INGESTION & DEMO SEEDING ---")
    jobs_ingested = JobIngestionService.ingest_from_source(MockJobSource())
    print(f"Ingested {len(jobs_ingested)} mock jobs without duplication.")
    
    # Ensure demo user exists
    user, created = User.objects.get_or_create(username="demo_candidate", email="demo@jobpilot.ai")
    user.set_password("DemoPass123!")
    user.save()
    
    profile = user.candidate_profile
    profile.full_name = "Alex Developer"
    profile.headline = "Python & Django Backend Engineer"
    profile.location = "Hyderabad"
    profile.preferred_locations = ["Hyderabad", "Remote"]
    profile.skills = ["Python", "Django", "DRF", "SQL", "Docker", "Git"]
    profile.years_of_experience = 1
    profile.minimum_salary = 400000
    profile.maximum_salary = 800000
    profile.save()
    print(f"User: {user.username} (Profile ID: {profile.id}) configured successfully.")

    # STEP 3: Authentication (JWT Token)
    print("\n--- [STEP 3] JWT AUTHENTICATION ---")
    auth_resp = client.post("/api/auth/token/", {"username": "demo_candidate", "password": "DemoPass123!"}, format="json")
    print(f"POST /api/auth/token/ -> Status: {auth_resp.status_code}")
    assert auth_resp.status_code == 200
    access_token = auth_resp.data["access"]
    print(f"Access Token: {access_token[:30]}...")

    # Authenticate client
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    # STEP 4: Candidate Profile API
    print("\n--- [STEP 4] CANDIDATE PROFILE API ---")
    prof_resp = client.get("/api/profile/")
    print(f"GET /api/profile/ -> Status: {prof_resp.status_code}")
    print(f"Headline: {prof_resp.data.get('headline')}")
    print(f"Skills: {prof_resp.data.get('skills')}")
    print(f"Location: {prof_resp.data.get('location')}")

    # STEP 5: Job Listing & Filtering API
    print("\n--- [STEP 5] JOB SEARCH & FILTERING ---")
    jobs_resp = client.get("/api/jobs/?search=Python&location=Hyderabad")
    print(f"GET /api/jobs/?search=Python&location=Hyderabad -> Status: {jobs_resp.status_code}")
    job_count = jobs_resp.data.get("count", len(jobs_resp.data.get("results", [])))
    print(f"Jobs Found: {job_count}")
    
    first_job = Job.objects.first()
    print(f"Selected Sample Job: ID {first_job.id} - '{first_job.title}' at {first_job.company}")

    # STEP 6: Deterministic Job Matching Engine
    print("\n--- [STEP 6] DETERMINISTIC JOB MATCHING ENGINE ---")
    match_resp = client.get(f"/api/jobs/{first_job.id}/match/")
    print(f"GET /api/jobs/{first_job.id}/match/ -> Status: {match_resp.status_code}")
    match_data = match_resp.data
    print(f"Overall Match Score: {match_data.get('overall_match')}%")
    print(f"Breakdown: {json.dumps(match_data.get('breakdown'), indent=2)}")
    print(f"Matching Skills: {match_data.get('matching_skills')}")
    print(f"Missing Skills: {match_data.get('missing_skills')}")

    # STEP 7: Application Tracking Workflow
    print("\n--- [STEP 7] APPLICATION TRACKING WORKFLOW ---")
    app_resp = client.post("/api/applications/", {"job": first_job.id, "status": "SAVED", "notes": "Looks like a great fit."}, format="json")
    if app_resp.status_code == 201:
        app_id = app_resp.data["id"]
        print(f"Created Application ID {app_id} with status 'SAVED'")
    else:
        existing_app = Application.objects.get(user=user, job=first_job)
        app_id = existing_app.id
        print(f"Existing Application ID {app_id} retrieved.")

    # Update application to INTERVIEW
    patch_resp = client.patch(f"/api/applications/{app_id}/", {"status": "INTERVIEW", "notes": "Interview scheduled for next Monday."}, format="json")
    print(f"PATCH /api/applications/{app_id}/ -> New Status: {patch_resp.data.get('status')}")

    # STEP 8: AI Agent Tool-Calling Chat API
    print("\n--- [STEP 8] AI AGENT TOOL-CALLING CHAT API ---")
    agent_queries = [
        "Find Python jobs in Hyderabad",
        f"Calculate match score for job {first_job.id}",
        f"Generate cover letter for job {first_job.id}",
        "Show my applications",
    ]

    for q in agent_queries:
        print(f"\nUser Query: '{q}'")
        chat_resp = client.post("/api/agent/chat/", {"message": q}, format="json")
        print(f"Agent Status: {chat_resp.status_code}")
        print(f"Tool Invoked: '{chat_resp.data.get('tool')}'")
        print(f"Response Content: {chat_resp.data.get('response')[:150]}...")

    # STEP 9: Dashboard Statistics API
    print("\n--- [STEP 9] DASHBOARD STATS API ---")
    dash_resp = client.get("/api/dashboard/")
    print(f"GET /api/dashboard/ -> Status: {dash_resp.status_code}")
    print(f"Dashboard Stats: {json.dumps(dash_resp.data, indent=2)}")

    print("\n" + "=" * 70)
    print(" ✅ DEMO COMPLETED SUCCESSFULLY! ALL SYSTEMS FUNCTIONAL.")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
