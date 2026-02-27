from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import home
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from courses.views import CategoryViewSet, CourseViewSet, ModuleViewSet, LectureViewSet
from enrollments.views import EnrollmentViewSet, LectureProgressViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("courses", CourseViewSet)
router.register("modules", ModuleViewSet)
router.register("lectures", LectureViewSet)
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("progress", LectureProgressViewSet, basename="progress")

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),

    # JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Include Dashboard URLs with api/ prefix
    path("api/", include('dashboard.urls')),
    
    # Include Reviews URLs with api/ prefix
    path("api/", include('reviews.urls')),

    # All API routes from router (already under api/)
    path("api/", include(router.urls)),
]