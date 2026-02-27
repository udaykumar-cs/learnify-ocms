from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Enrollment, LectureProgress
from .serializers import EnrollmentSerializer, LectureProgressSerializer
from rest_framework.exceptions import PermissionDenied


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data["course"]

        # ✅ Role restriction
        if user.role != "STUDENT":
            raise PermissionDenied("Only students can enroll in courses.")

        # ✅ Prevent duplicate enrollment
        if Enrollment.objects.filter(student=user, course=course).exists():
            raise PermissionDenied("You are already enrolled in this course.")

        serializer.save(student=user)

class LectureProgressViewSet(viewsets.ModelViewSet):
    serializer_class = LectureProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LectureProgress.objects.filter(
            enrollment__student=self.request.user
        )

    def perform_create(self, serializer):
        user = self.request.user
        lecture = serializer.validated_data["lecture"]

        # ✅ Only students allowed
        if user.role != "STUDENT":
            raise PermissionDenied("Only students can track lecture progress.")

        # ✅ Check enrollment
        enrollment = Enrollment.objects.filter(
            student=user,
            course=lecture.module.course
        ).first()

        if not enrollment:
            raise PermissionDenied("You must be enrolled in this course.")

        # ✅ Prevent duplicate progress
        if LectureProgress.objects.filter(
            enrollment=enrollment,
            lecture=lecture
        ).exists():
            raise PermissionDenied("Progress already exists for this lecture.")

        serializer.save(enrollment=enrollment)