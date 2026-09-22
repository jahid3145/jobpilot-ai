from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.resumes.models import Resume

from .models import Job
from .serializers import JobSerializer
from .services import JobMatchingService


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobSerializer
    filterset_fields = ("location", "employment_type", "is_active", "source")
    search_fields = ("title", "company", "description", "location")
    ordering_fields = ("posted_at", "salary_min", "salary_max", "experience_min", "collected_at")
    ordering = ("-collected_at",)

    def get_queryset(self):
        queryset = super().get_queryset()
        minimum_salary = self.request.query_params.get("min_salary")
        maximum_salary = self.request.query_params.get("max_salary")
        experience = self.request.query_params.get("experience")
        skill = self.request.query_params.get("skill")
        if minimum_salary:
            queryset = queryset.filter(salary_max__gte=minimum_salary)
        if maximum_salary:
            queryset = queryset.filter(salary_min__lte=maximum_salary)
        if experience:
            queryset = queryset.filter(experience_min__lte=experience)
        if skill:
            queryset = queryset.filter(required_skills__icontains=skill)
        return queryset

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        if not (self.request.user.is_staff or serializer.instance.created_by_id == self.request.user.id):
            raise PermissionDenied("You can only modify jobs you created.")
        serializer.save()

    def perform_destroy(self, instance):
        if not (self.request.user.is_staff or instance.created_by_id == self.request.user.id):
            raise PermissionDenied("You can only delete jobs you created.")
        instance.delete()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def match(self, request, pk=None):
        job = self.get_object()
        resume = Resume.objects.filter(user=request.user, is_primary=True).first()
        return Response(JobMatchingService(request.user.candidate_profile, resume).calculate_match(job))
