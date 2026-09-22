from pathlib import Path

from rest_framework import serializers

from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"
        read_only_fields = ("user", "extracted_text", "uploaded_at", "updated_at")

    def validate_file(self, uploaded_file):
        if uploaded_file.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Resume files must be 5 MB or smaller.")
        if Path(uploaded_file.name).suffix.lower() != ".pdf":
            raise serializers.ValidationError("Only PDF resumes are accepted.")
        return uploaded_file

