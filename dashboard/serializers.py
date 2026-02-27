from rest_framework import serializers
from courses.models import Course, Category
from accounts.models import User
from enrollments.models import Enrollment

class DashboardStatsSerializer(serializers.Serializer):
    # Overview stats
    total_courses = serializers.IntegerField()
    published_courses = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_instructors = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    recent_enrollments = serializers.IntegerField()
    
    # For charts/graphs
    courses_by_category = serializers.ListField(child=serializers.DictField())
    enrollments_over_time = serializers.ListField(child=serializers.DictField())

class CourseListDashboardSerializer(serializers.ModelSerializer):
    """For the course table in UI"""
    instructor_name = serializers.CharField(source='instructor.full_name')
    category_name = serializers.CharField(source='category.name')
    students_count = serializers.IntegerField(source='enrollments.count')
    status = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display')
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'level_display', 'price', 
            'category_name', 'instructor_name', 'students_count',
            'status', 'is_published', 'created_at'
        ]
    
    def get_status(self, obj):
        return "Published" if obj.is_published else "Draft"

class InstructorDashboardSerializer(serializers.Serializer):
    """For instructor view"""
    my_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_revenue = serializers.FloatField()
    average_rating = serializers.FloatField()
    recent_enrollments = serializers.ListField(child=serializers.DictField())

class StudentDashboardSerializer(serializers.Serializer):
    """For student view"""
    enrolled_courses = serializers.IntegerField()
    completed_courses = serializers.IntegerField()
    in_progress_courses = serializers.IntegerField()
    overall_progress = serializers.FloatField()
    certificates_earned = serializers.IntegerField()
    recent_activities = serializers.ListField(child=serializers.DictField())