from rest_framework import serializers

from .models import Application, CoverLetter


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    company = serializers.CharField(source="job.company", read_only=True)

    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")

    def validate_job(self, job):
        user = self.context["request"].user
        queryset = Application.objects.filter(user=user, job=job)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("You already track this job.")
        return job


class CoverLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverLetter
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")

