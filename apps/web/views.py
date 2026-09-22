from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.ai_agent.tools import explain_job_match, list_applications, search_jobs
from apps.applications.models import Application
from apps.jobs.models import Job
from apps.jobs.services import JobMatchingService
from apps.resumes.models import Resume
from apps.resumes.services import ResumeParser

from .forms import CandidateProfileForm, RegistrationForm, ResumeUploadForm


def home(request):
    return render(request, "web/home.html")


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your JobPilot account is ready. Complete your profile to get better matches.")
        return redirect("profile")
    return render(request, "registration/register.html", {"form": form})


def _matcher_for(user):
    resume = Resume.objects.filter(user=user, is_primary=True).first()
    return JobMatchingService(user.candidate_profile, resume)


@login_required
def dashboard(request):
    applications = Application.objects.select_related("job").filter(user=request.user)
    matcher = _matcher_for(request.user)
    recommendations = []
    for job in Job.objects.filter(is_active=True)[:30]:
        recommendations.append({"job": job, "match": matcher.calculate_match(job)})
    recommendations.sort(key=lambda item: item["match"]["overall_match"], reverse=True)
    status_counts = {item["status"]: item["count"] for item in applications.values("status").annotate(count=Count("id"))}
    follow_ups = applications.filter(follow_up_date__lte=timezone.localdate()).exclude(
        status__in=[Application.Status.REJECTED, Application.Status.SELECTED, Application.Status.WITHDRAWN]
    )
    return render(
        request,
        "web/dashboard.html",
        {
            "recommendations": recommendations[:5],
            "application_count": applications.count(),
            "status_counts": status_counts,
            "follow_ups": follow_ups[:5],
            "has_profile_skills": bool(request.user.candidate_profile.skills),
        },
    )


@login_required
def profile(request):
    form = CandidateProfileForm(request.POST or None, instance=request.user.candidate_profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your candidate profile has been updated.")
        return redirect("dashboard")
    return render(request, "web/profile.html", {"form": form})


@login_required
def resume_list(request):
    form = ResumeUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            if form.cleaned_data["is_primary"]:
                Resume.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            parser = ResumeParser()
            try:
                resume.file.open("rb")
                extracted_text = parser.extract_pdf_text(resume.file)
                resume.extracted_text = extracted_text
                resume.parsed_data = parser.parse(extracted_text)
                resume.save(update_fields=("extracted_text", "parsed_data", "updated_at"))
                messages.success(request, "Resume uploaded and parsed successfully.")
            except Exception:
                messages.warning(request, "Resume was uploaded, but text extraction failed. You can still update your profile manually.")
            finally:
                resume.file.close()
        return redirect("resumes")
    return render(request, "web/resumes.html", {"form": form, "resumes": Resume.objects.filter(user=request.user)})


@login_required
def jobs(request):
    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    job_list = Job.objects.filter(is_active=True)
    if query:
        job_list = job_list.filter(title__icontains=query)
    if location:
        job_list = job_list.filter(location__icontains=location)
    matcher = _matcher_for(request.user)
    result_rows = [{"job": job, "match": matcher.calculate_match(job)} for job in job_list[:50]]
    result_rows.sort(key=lambda item: item["match"]["overall_match"], reverse=True)
    return render(request, "web/jobs.html", {"jobs": result_rows, "query": query, "location": location})


@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, pk=job_id, is_active=True)
    application = Application.objects.filter(user=request.user, job=job).first()
    return render(request, "web/job_detail.html", {"job": job, "match": _matcher_for(request.user).calculate_match(job), "application": application})


@login_required
@require_http_methods(["POST"])
def save_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id, is_active=True)
    application, created = Application.objects.get_or_create(user=request.user, job=job, defaults={"status": Application.Status.SAVED})
    messages.success(request, "Job saved to your tracker." if created else "This job is already in your tracker.")
    return redirect("job-detail", job_id=job.id)


@login_required
def applications(request):
    items = Application.objects.select_related("job").filter(user=request.user)
    return render(request, "web/applications.html", {"applications": items, "statuses": Application.Status.choices})


@login_required
@require_http_methods(["POST"])
def update_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id, user=request.user)
    valid_statuses = {choice[0] for choice in Application.Status.choices}
    new_status = request.POST.get("status")
    if new_status not in valid_statuses:
        raise Http404
    application.status = new_status
    application.notes = request.POST.get("notes", application.notes)
    follow_up = request.POST.get("follow_up_date")
    application.follow_up_date = follow_up or None
    if new_status == Application.Status.APPLIED and not application.applied_at:
        application.applied_at = timezone.now()
    application.save()
    messages.success(request, "Application updated.")
    return redirect("applications")


@login_required
@require_http_methods(["GET", "POST"])
def assistant(request):
    result = None
    message = ""
    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        lowered_message = message.lower()
        if "application" in lowered_message:
            result = {"tool": "list_applications", "data": list_applications(request.user), "is_list": True}
        elif "match" in lowered_message or "missing" in lowered_message:
            result = {"tool": "help", "data": "Open a job card to see its transparent score and missing skills.", "is_list": False}
        else:
            result = {
                "tool": "search_jobs",
                "data": search_jobs(request.user, query="django" if "django" in lowered_message else "python" if "python" in lowered_message else "", location="hyderabad" if "hyderabad" in lowered_message else ""),
                "is_list": True,
            }
    return render(request, "web/assistant.html", {"result": result, "message": message})
