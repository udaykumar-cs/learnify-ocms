from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Avg
from .models import Review
from .serializers import ReviewSerializer
from courses.models import Course

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Review model
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter reviews based on user role"""
        user = self.request.user
        
        if user.role == 'ADMIN':
            return Review.objects.all()
        elif user.role == 'INSTRUCTOR':
            # Instructors see reviews for their courses
            return Review.objects.filter(course__instructor=user)
        else:  # STUDENT
            # Students see their own reviews
            return Review.objects.filter(student=user)

    def perform_create(self, serializer):
        """Create review with current student"""
        serializer.save(student=self.request.user)

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews"""
        reviews = Review.objects.filter(student=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='course/(?P<course_id>[^/.]+)')
    def course_reviews(self, request, course_id=None):
        """Get all reviews for a specific course"""
        try:
            course = Course.objects.get(id=course_id)
            reviews = Review.objects.filter(course=course)
            
            # Calculate rating distribution
            distribution = reviews.values('rating').annotate(
                count=Count('id')
            ).order_by('rating')
            
            summary = {
                'average_rating': course.average_rating,
                'total_reviews': course.total_reviews,
                'rating_distribution': {
                    str(item['rating']): item['count'] 
                    for item in distribution
                }
            }
            
            serializer = self.get_serializer(reviews, many=True)
            return Response({
                'reviews': serializer.data,
                'summary': summary
            })
        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], url_path='course/(?P<course_id>[^/.]+)/summary')
    def review_summary(self, request, course_id=None):
        """Get just the summary for a course"""
        try:
            course = Course.objects.get(id=course_id)
            
            distribution = Review.objects.filter(course=course).values(
                'rating'
            ).annotate(
                count=Count('id')
            ).order_by('rating')
            
            summary = {
                'average_rating': course.average_rating,
                'total_reviews': course.total_reviews,
                'rating_distribution': {
                    str(item['rating']): item['count'] 
                    for item in distribution
                }
            }
            
            return Response(summary)
        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )