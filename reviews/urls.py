from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Course-specific review endpoints
    path('courses/<uuid:course_id>/reviews/', 
         views.ReviewViewSet.as_view({'get': 'course_reviews', 'post': 'create'}), 
         name='course-reviews'),
    path('courses/<uuid:course_id>/reviews/summary/', 
         views.ReviewViewSet.as_view({'get': 'review_summary'}), 
         name='course-review-summary'),
    
    # User's own reviews
    path('reviews/my/', 
         views.ReviewViewSet.as_view({'get': 'my_reviews'}), 
         name='my-reviews'),
]