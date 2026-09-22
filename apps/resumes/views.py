from django.db import transaction
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Resume
from .serializers import ResumeSerializer
from .services import ResumeParser


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            if serializer.validated_data.get("is_primary"):
                Resume.objects.filter(user=self.request.user, is_primary=True).update(is_primary=False)
            resume = serializer.save(user=self.request.user)
            if resume.file:
                parser = ResumeParser()
                try:
                    resume.file.open("rb")
                    extracted_text = parser.extract_pdf_text(resume.file)
                    resume.extracted_text = extracted_text
                    resume.parsed_data = parser.parse(extracted_text)
                    resume.save(update_fields=("extracted_text", "parsed_data", "updated_at"))
                finally:
                    resume.file.close()

    def perform_update(self, serializer):
        with transaction.atomic():
            if serializer.validated_data.get("is_primary"):
                Resume.objects.filter(user=self.request.user, is_primary=True).exclude(pk=self.get_object().pk).update(is_primary=False)
            resume = serializer.save()

    @action(detail=True, methods=["post"])
    def set_primary(self, request, pk=None):
        with transaction.atomic():
            Resume.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
            resume = self.get_object()
            resume.is_primary = True
            resume.save(update_fields=("is_primary", "updated_at"))
        return Response(self.get_serializer(resume).data)
