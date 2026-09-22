from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Returns a lightweight status response for uptime checks."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "jobpilot-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckView.as_view(), name="health-check"),
    path("api/", include("apps.users.urls")),
    path("api/", include("apps.resumes.urls")),
    path("api/", include("apps.jobs.urls")),
    path("api/", include("apps.applications.urls")),
    path("api/", include("apps.ai_agent.urls")),
    path("api/", include("apps.notifications.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="api-docs"),
    path("", include("apps.web.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
