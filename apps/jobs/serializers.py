from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = ("created_by", "collected_at")

    def validate(self, attrs):
        minimum = attrs.get("salary_min", getattr(self.instance, "salary_min", None))
        maximum = attrs.get("salary_max", getattr(self.instance, "salary_max", None))
        if minimum and maximum and minimum > maximum:
            raise serializers.ValidationError("Salary maximum must be greater than or equal to salary minimum.")
        return attrs

