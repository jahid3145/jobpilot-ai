from rest_framework.routers import DefaultRouter

from .views import ApplicationViewSet, CoverLetterViewSet

router = DefaultRouter()
router.register("applications", ApplicationViewSet, basename="application")
router.register("cover-letters", CoverLetterViewSet, basename="cover-letter")

urlpatterns = router.urls

