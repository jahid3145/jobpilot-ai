from apps.applications.models import Application
from apps.applications.services import CoverLetterService
from apps.jobs.models import Job
from apps.jobs.services import JobMatchingService
from apps.resumes.models import Resume
from .ai_service import DemoAIService


def search_jobs(user, query="", role="", location="", min_salary=None, max_salary=None, experience=""):
    """Tool 1: search_jobs"""
    jobs = Job.objects.filter(is_active=True)
    q = query or role
    if q:
        jobs = jobs.filter(title__icontains=q)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if min_salary:
        jobs = jobs.filter(salary_max__gte=min_salary)
    if max_salary:
        jobs = jobs.filter(salary_min__lte=max_salary)

    items = [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "salary_min": float(job.salary_min) if job.salary_min else None,
            "salary_max": float(job.salary_max) if job.salary_max else None,
        }
        for job in jobs[:10]
    ]
    return {"success": True, "data": {"total": len(items), "jobs": items}}


def get_job_details(user, job_id):
    """Tool 2: get_job_details"""
    job = Job.objects.filter(pk=job_id, is_active=True).first()
    if not job:
        return {"success": False, "error": "Job not found."}
    return {
        "success": True,
        "data": {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "required_skills": job.required_skills,
            "preferred_skills": job.preferred_skills,
            "salary_min": float(job.salary_min) if job.salary_min else None,
            "salary_max": float(job.salary_max) if job.salary_max else None,
            "external_url": job.external_url,
        },
    }


def get_candidate_profile(user):
    """Tool 3: get_candidate_profile"""
    profile = getattr(user, "candidate_profile", None)
    if not profile:
        return {"success": False, "error": "Candidate profile not found."}
    return {
        "success": True,
        "data": {
            "full_name": profile.full_name,
            "headline": profile.headline,
            "location": profile.location,
            "years_experience": profile.years_of_experience,
            "skills": profile.skills,
            "preferred_locations": profile.preferred_locations,
            "minimum_salary": float(profile.minimum_salary) if profile.minimum_salary else None,
            "maximum_salary": float(profile.maximum_salary) if profile.maximum_salary else None,
        },
    }


def get_primary_resume(user):
    """Tool 4: get_primary_resume"""
    resume = Resume.objects.filter(user=user, is_primary=True).first()
    if not resume:
        return {"success": False, "error": "No primary resume found."}
    return {
        "success": True,
        "data": {
            "id": resume.id,
            "title": resume.title,
            "parsed_data": resume.parsed_data,
            "uploaded_at": resume.uploaded_at.isoformat(),
        },
    }


def calculate_job_match(user, job_id):
    """Tool 5: calculate_job_match"""
    job = Job.objects.filter(pk=job_id, is_active=True).first()
    if not job:
        return {"success": False, "error": "Job not found."}
    resume = Resume.objects.filter(user=user, is_primary=True).first()
    match_data = JobMatchingService(user.candidate_profile, resume).calculate_match(job)
    return {"success": True, "data": match_data}


def explain_job_match(user, job_id):
    """Tool 6: explain_job_match"""
    match_res = calculate_job_match(user, job_id)
    if not match_res.get("success"):
        return match_res
    match = match_res["data"]
    explanation = DemoAIService().explain_match(match)
    return {"success": True, "data": {"match": match, "explanation": explanation}}


def generate_cover_letter(user, job_id):
    """Tool 7: generate_cover_letter"""
    job = Job.objects.filter(pk=job_id, is_active=True).first()
    if not job:
        return {"success": False, "error": "Job not found."}
    resume = Resume.objects.filter(user=user, is_primary=True).first()
    letter = CoverLetterService().generate(user.candidate_profile, resume, job)
    return {"success": True, "data": {"job_id": job.id, "cover_letter": letter}}


def save_job(user, job_id):
    """Tool 8: save_job"""
    job = Job.objects.filter(pk=job_id, is_active=True).first()
    if not job:
        return {"success": False, "error": "Job not found."}
    app, created = Application.objects.get_or_create(user=user, job=job, defaults={"status": "SAVED"})
    return {"success": True, "data": {"application_id": app.id, "status": app.status, "created": created}}


def create_application(user, job_id, status="APPLIED", notes=""):
    """Tool 9: create_application"""
    job = Job.objects.filter(pk=job_id, is_active=True).first()
    if not job:
        return {"success": False, "error": "Job not found."}
    if Application.objects.filter(user=user, job=job).exists():
        return {"success": False, "error": "Application already exists for this job."}
    app = Application.objects.create(user=user, job=job, status=status, notes=notes)
    return {"success": True, "data": {"application_id": app.id, "status": app.status}}


def update_application_status(user, application_id, status, notes=""):
    """Tool 10: update_application_status"""
    app = Application.objects.filter(pk=application_id, user=user).first()
    if not app:
        return {"success": False, "error": "Application not found."}
    app.status = status
    if notes:
        app.notes = notes
    app.save()
    return {"success": True, "data": {"application_id": app.id, "status": app.status}}


def list_applications(user, status=None):
    """Tool 11: list_applications"""
    apps = Application.objects.select_related("job").filter(user=user)
    if status:
        apps = apps.filter(status=status)
    items = [
        {
            "id": item.id,
            "job_id": item.job.id,
            "title": item.job.title,
            "company": item.job.company,
            "status": item.status,
            "applied_at": item.applied_at.isoformat() if item.applied_at else None,
            "follow_up_date": item.follow_up_date.isoformat() if item.follow_up_date else None,
        }
        for item in apps[:20]
    ]
    return {"success": True, "data": {"total": len(items), "applications": items}}


def find_follow_up_tasks(user):
    """Tool 12: find_follow_up_tasks"""
    apps = Application.objects.select_related("job").filter(user=user, follow_up_date__isnull=False)
    items = [
        {
            "application_id": item.id,
            "job_title": item.job.title,
            "company": item.job.company,
            "status": item.status,
            "follow_up_date": item.follow_up_date.isoformat(),
        }
        for item in apps
    ]
    return {"success": True, "data": {"pending_follow_ups": len(items), "tasks": items}}


# Tool aliases for test compatibility
search_jobs_tool = search_jobs
calculate_job_match_tool = calculate_job_match
generate_cover_letter_tool = generate_cover_letter
list_applications_tool = list_applications


