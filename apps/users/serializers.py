from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import CandidateProfile

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "password")
        read_only_fields = ("id",)

    def validate_email(self, value):
        normalized_email = value.strip().lower()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return normalized_email

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        exclude = ("user",)

    def validate(self, attrs):
        minimum_salary = attrs.get("minimum_salary", getattr(self.instance, "minimum_salary", None))
        maximum_salary = attrs.get("maximum_salary", getattr(self.instance, "maximum_salary", None))
        if minimum_salary and maximum_salary and minimum_salary > maximum_salary:
            raise serializers.ValidationError("Maximum salary must be greater than or equal to minimum salary.")
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        from rest_framework_simplejwt.tokens import RefreshToken

        RefreshToken(self.validated_data["refresh"]).blacklist()
