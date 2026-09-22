from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CandidateProfileView, CurrentUserView, LogoutView, RegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="api-register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="token-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="current-user"),
    path("profile/", CandidateProfileView.as_view(), name="candidate-profile"),
]
