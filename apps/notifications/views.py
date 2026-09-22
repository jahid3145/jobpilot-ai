from django.db.models import Count
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.models import Application
from apps.jobs.models import Job
from apps.jobs.services import JobMatchingService
from apps.resumes.models import Resume


class FollowUpView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        applications = Application.objects.select_related("job").filter(
            user=request.user,
            follow_up_date__lte=timezone.localdate(),
        ).exclude(status__in=[Application.Status.REJECTED, Application.Status.SELECTED, Application.Status.WITHDRAWN])
        return Response(
            [
                {
                    "id": application.id,
                    "job": application.job.title,
                    "company": application.job.company,
                    "status": application.status,
                    "follow_up_date": application.follow_up_date,
                }
                for application in applications
            ]
        )


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        applications = Application.objects.filter(user=request.user)
        resume = Resume.objects.filter(user=request.user, is_primary=True).first()
        matcher = JobMatchingService(request.user.candidate_profile, resume)
        ranked_jobs = []
        missing_skills = []
        for job in Job.objects.filter(is_active=True)[:50]:
            result = matcher.calculate_match(job)
            ranked_jobs.append({"id": job.id, "title": job.title, "company": job.company, **result})
            missing_skills.extend(result["missing_skills"])
        ranked_jobs.sort(key=lambda item: item["overall_match"], reverse=True)
        status_counts = {item["status"]: item["count"] for item in applications.values("status").annotate(count=Count("id"))}
        return Response(
            {
                "total_saved_jobs": applications.filter(status=Application.Status.SAVED).count(),
                "applications": applications.count(),
                "applications_by_status": status_counts,
                "pending_follow_ups": applications.filter(follow_up_date__lte=timezone.localdate()).exclude(
                    status__in=[Application.Status.REJECTED, Application.Status.SELECTED, Application.Status.WITHDRAWN]
                ).count(),
                "top_matching_jobs": ranked_jobs[:5],
                "most_common_missing_skills": sorted(set(missing_skills))[:10],
            }
        )

