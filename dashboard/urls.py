
from django.urls import path
from . import views

urlpatterns = [
    path('admin/analytics/', views.admin_analytics, name='admin-analytics'),
    path('admin/top-courses/', views.top_courses, name='top-courses'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor-dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student-dashboard'),
    
    # Add this line for dashboard/stats/
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]