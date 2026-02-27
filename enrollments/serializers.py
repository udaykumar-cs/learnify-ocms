from rest_framework import serializers
from .models import Enrollment, LectureProgress


from rest_framework import serializers
from .models import Enrollment

from django.utils import timezone
from courses.models import Lecture

class EnrollmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ["student"]

    def validate(self, data):
        user = self.context["request"].user
        course = data.get("course")

        if Enrollment.objects.filter(student=user, course=course).exists():
            raise serializers.ValidationError(
                "You are already enrolled in this course."
            )

        return data



class LectureProgressSerializer(serializers.ModelSerializer):

    class Meta:
        model = LectureProgress
        fields = ["id", "lecture", "completed", "completed_at"]
        read_only_fields = ["completed_at"]

    def validate(self, data):
        request = self.context["request"]
        user = request.user

        lecture = data.get("lecture")

        # enrollment will be injected from view
        enrollment = self.context.get("enrollment")

        if not enrollment:
            raise serializers.ValidationError("Enrollment not found.")

        if enrollment.student != user:
            raise serializers.ValidationError(
                "You can only update your own progress."
            )

        if lecture.module.course != enrollment.course:
            raise serializers.ValidationError(
                "Lecture does not belong to your enrolled course."
            )

        return data

    def create(self, validated_data):
        if validated_data.get("completed"):
            validated_data["completed_at"] = timezone.now()

        progress_obj = super().create(validated_data)

        self.update_enrollment_progress(progress_obj.enrollment)

        return progress_obj
    