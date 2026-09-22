from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializers import CandidateProfileSerializer, LogoutSerializer, RegistrationSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        from rest_framework_simplejwt.tokens import RefreshToken

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": serializer.data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "message": "Account created successfully.",
            },
            status=201,
        )



class CandidateProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CandidateProfileSerializer

    def get_object(self):
        return self.request.user.candidate_profile


class CurrentUserView(generics.GenericAPIView):
    def get(self, request):
        return Response({"id": request.user.id, "username": request.user.username, "email": request.user.email})


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=400)
        return Response(status=204)
