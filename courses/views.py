from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Category, Course, Module, Lecture
from .permissions import IsInstructorOrReadOnly

from .serializers import (
    CategorySerializer,
    CourseSerializer,
    ModuleSerializer,
    LectureSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsInstructorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)
    def perform_create(self, serializer):
        user = self.request.user

        if user.role not in ["ADMIN", "INSTRUCTOR"]:
            raise PermissionDenied("Only instructors can create courses.")

        serializer.save(instructor=user)

    def perform_update(self, serializer):
        course = self.get_object()
        user = self.request.user

        if user.role == "ADMIN":
            serializer.save()
        elif user.role == "INSTRUCTOR" and course.instructor == user:
            serializer.save()
        else:
            raise PermissionDenied("You cannot edit this course.")

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role == "ADMIN":
            instance.delete()
        elif user.role == "INSTRUCTOR" and instance.instructor == user:
            instance.delete()
        else:
            raise PermissionDenied("You cannot delete this course.")

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [AllowAny]


class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [AllowAny]
