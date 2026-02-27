from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_avatar = serializers.ImageField(source='student.avatar', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'course', 'student', 'student_name', 'student_avatar',
            'rating', 'comment', 'created_at', 'updated_at', 'time_ago'
        ]
        read_only_fields = ['student', 'created_at', 'updated_at']

    def get_time_ago(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.created_at) + " ago"

    def validate(self, data):
        request = self.context.get('request')
        course = data.get('course')
        
        # Check if user is student
        if request.user.role != 'STUDENT':
            raise serializers.ValidationError("Only students can review courses")
        
        # Check if already reviewed
        if not self.instance and Review.objects.filter(
            course=course, 
            student=request.user
        ).exists():
            raise serializers.ValidationError("You have already reviewed this course")
        
        return data

class CourseReviewSummarySerializer(serializers.Serializer):
    """For displaying course rating summary"""
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField()