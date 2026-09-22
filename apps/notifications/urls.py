from django.urls import path

from .views import DashboardView, FollowUpView

urlpatterns = [
    path("notifications/follow-ups/", FollowUpView.as_view(), name="follow-ups"),
    path("dashboard/", DashboardView.as_view(), name="api-dashboard"),
]
