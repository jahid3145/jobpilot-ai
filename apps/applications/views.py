from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.resumes.models import Resume

from .models import Application, CoverLetter
from .serializers import ApplicationSerializer, CoverLetterSerializer
from .services import CoverLetterService


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ("status",)
    ordering_fields = ("created_at", "updated_at", "follow_up_date", "applied_at")

    def get_queryset(self):
        return Application.objects.select_related("job").filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CoverLetterViewSet(viewsets.ModelViewSet):
    serializer_class = CoverLetterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CoverLetter.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"])
    def generate(self, request):
        job_id = request.data.get("job_id")
        if not job_id:
            return Response({"detail": "job_id is required."}, status=400)
        from apps.jobs.models import Job

        job = Job.objects.filter(pk=job_id, is_active=True).first()
        if not job:
            return Response({"detail": "Job not found."}, status=404)
        resume = Resume.objects.filter(user=request.user, is_primary=True).first()
        content = CoverLetterService().generate(request.user.candidate_profile, resume, job)
        letter = CoverLetter.objects.create(user=request.user, job=job, content=content)
        return Response(self.get_serializer(letter).data, status=201)

