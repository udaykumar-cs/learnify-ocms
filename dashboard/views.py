from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.utils.timesince import timesince
from datetime import timedelta
from django.core.cache import cache
from django.conf import settings

# Model imports
from courses.models import Course, Category, Lecture  # Added Lecture
from accounts.models import User
from enrollments.models import Enrollment, LectureProgress
from reviews.models import Review

# Redis cache keys
CACHE_TOP_COURSES = 'dashboard_top_courses'
CACHE_ADMIN_STATS = 'dashboard_admin_stats'
CACHE_TIMEOUT = 3600  # 1 hour

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_analytics(request):
    """Admin analytics API - matches wireframe"""
    if request.user.role != 'ADMIN':
        return Response(
            {"error": "Only admins can access analytics"},
            status=403
        )
    
    # Try to get from cache first
    cached_data = cache.get(f"{CACHE_ADMIN_STATS}_{request.GET.get('period', 'day')}")
    if cached_data:
        return Response(cached_data)
    
    # Time periods
    today = timezone.now()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # Calculate all stats
    stats = {
        # Top stats cards (from wireframe)
        'total_users': User.objects.count(),
        'total_courses': Course.objects.count(),
        'total_enrollments': Enrollment.objects.count(),
        'total_revenue': Enrollment.objects.aggregate(
            total=Sum('course__price')
        )['total'] or 0,
        
        # User breakdown
        'students_count': User.objects.filter(role='STUDENT').count(),
        'instructors_count': User.objects.filter(role='INSTRUCTOR').count(),
        
        # Course stats
        'published_courses': Course.objects.filter(is_published=True).count(),
        'categories_count': Category.objects.count(),
        
        # Recent activity
        'recent_enrollments': Enrollment.objects.filter(
            enrolled_at__gte=last_7_days
        ).count(),
        'recent_reviews': Review.objects.filter(
            created_at__gte=last_7_days
        ).count(),
        
        # Platform insights (from wireframe)
        'completion_rate': calculate_completion_rate(),
        'average_course_rating': Review.objects.aggregate(
            avg=Avg('rating')
        )['avg'] or 0,
        
        # Trends
        'enrollment_trend': get_enrollment_trend(7),
        'revenue_trend': get_revenue_trend(7),
    }
    
    # Cache for 1 hour
    cache.set(f"{CACHE_ADMIN_STATS}_{request.GET.get('period', 'day')}", stats, CACHE_TIMEOUT)
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_courses(request):
    """Top enrolled courses API - Redis cached"""
    if request.user.role != 'ADMIN':
        return Response(
            {"error": "Only admins can access top courses"},
            status=403
        )
    
    # Try cache first
    cached_courses = cache.get(CACHE_TOP_COURSES)
    if cached_courses:
        return Response(cached_courses)
    
    # Get top courses by enrollment count
    top_courses = Course.objects.filter(is_published=True).annotate(
        enrollment_count=Count('enrollments'),
        completion_count=Count(
            'enrollments',
            filter=Q(enrollments__status='COMPLETED')
        ),
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-enrollment_count')[:10].values(
        'id', 'title', 'price', 'enrollment_count', 
        'completion_count', 'avg_rating', 'review_count',
        'instructor__full_name', 'category__name'
    )
    
    result = list(top_courses)
    
    # Cache for 1 hour
    cache.set(CACHE_TOP_COURSES, result, CACHE_TIMEOUT)
    
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Universal dashboard stats - returns role-specific dashboard data"""
    user = request.user
    
    if user.role == 'ADMIN':
        # Instead of calling the function directly, return its response
        response = admin_analytics(request._request)  # Pass the underlying HttpRequest
        return response
    elif user.role == 'INSTRUCTOR':
        response = instructor_dashboard(request._request)
        return response
    else:  # STUDENT
        response = student_dashboard(request._request)
        return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def instructor_dashboard(request):
    """Instructor dashboard API"""
    if request.user.role != 'INSTRUCTOR':
        return Response(
            {"error": "Only instructors can access this dashboard"},
            status=403
        )
    
    user = request.user
    courses = Course.objects.filter(instructor=user)
    course_ids = courses.values_list('id', flat=True)
    
    # Get enrollments for instructor's courses
    enrollments = Enrollment.objects.filter(course__in=course_ids)
    
    stats = {
        'total_courses': courses.count(),
        'published_courses': courses.filter(is_published=True).count(),
        'total_students': enrollments.values('student').distinct().count(),
        'active_students': enrollments.filter(status='ACTIVE').count(),
        'completed_students': enrollments.filter(status='COMPLETED').count(),
        'total_revenue': enrollments.aggregate(
            total=Sum('course__price')
        )['total'] or 0,
        'average_rating': Review.objects.filter(
            course__in=course_ids
        ).aggregate(avg=Avg('rating'))['avg'] or 0,
        'total_reviews': Review.objects.filter(course__in=course_ids).count(),
        
        # Recent enrollments
        'recent_enrollments': enrollments.select_related(
            'student', 'course'
        ).order_by('-enrolled_at')[:10].values(
            'student__full_name', 'student__email', 
            'course__title', 'enrolled_at', 'status'
        ),
        
        # Course list
        'my_courses': courses.annotate(
            student_count=Count('enrollments'),
            review_count=Count('reviews')
        ).values('id', 'title', 'is_published', 'price', 
                'student_count', 'review_count', 'average_rating'),
    }
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    """Student dashboard API"""
    if request.user.role != 'STUDENT':
        return Response(
            {"error": "Only students can access this dashboard"},
            status=403
        )
    
    user = request.user
    enrollments = Enrollment.objects.filter(student=user).select_related('course')
    
    # Get in-progress courses
    in_progress = enrollments.filter(status='ACTIVE', progress__lt=100)
    completed = enrollments.filter(status='COMPLETED')
    
    # Get recent activities
    recent_progress = LectureProgress.objects.filter(
        enrollment__in=enrollments,
        completed=True
    ).select_related(
        'lecture__module__course'
    ).order_by('-completed_at')[:10]
    
    stats = {
        'enrolled_count': enrollments.count(),
        'completed_count': completed.count(),
        'in_progress_count': in_progress.count(),
        'overall_progress': calculate_student_progress(user),
        
        # Continue learning (courses in progress)
        'continue_learning': [
            {
                'course_id': e.course.id,
                'course_title': e.course.title,
                'progress': e.progress,
                'next_lecture': get_next_lecture(e),
                'thumbnail': getattr(e.course, 'thumbnail', None)
            }
            for e in in_progress[:3]
        ],
        
        # Recent activities
        'recent_activities': [
            {
                'type': 'lecture_completed',
                'course': p.lecture.module.course.title,
                'lecture': p.lecture.title,
                'timestamp': p.completed_at,
                'time_ago': timesince(p.completed_at) + " ago"
            }
            for p in recent_progress
        ],
        
        # My courses list
        'my_courses': [
            {
                'id': e.course.id,
                'title': e.course.title,
                'progress': e.progress,
                'status': e.status,
                'enrolled_at': e.enrolled_at,
                'instructor': e.course.instructor.full_name,
                'thumbnail': getattr(e.course, 'thumbnail', None)
            }
            for e in enrollments
        ],
    }
    
    return Response(stats)

# Helper functions
def calculate_completion_rate():
    total = Enrollment.objects.count()
    if total == 0:
        return 0
    completed = Enrollment.objects.filter(status='COMPLETED').count()
    return round((completed / total) * 100, 2)

def calculate_student_progress(student):
    enrollments = Enrollment.objects.filter(student=student)
    if not enrollments.exists():
        return 0
    total_progress = sum(e.progress for e in enrollments)
    return round(total_progress / enrollments.count(), 2)

def get_enrollment_trend(days=7):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    enrollments = Enrollment.objects.filter(
        enrolled_at__gte=start_date
    ).extra(
        {'date': "date(enrolled_at)"}
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    return list(enrollments)

def get_revenue_trend(days=7):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    revenue = Enrollment.objects.filter(
        enrolled_at__gte=start_date
    ).extra(
        {'date': "date(enrolled_at)"}
    ).values('date').annotate(
        daily_revenue=Sum('course__price')
    ).order_by('date')
    
    return list(revenue)

def get_next_lecture(enrollment):
    """Get next incomplete lecture for a course"""
    completed_lectures = LectureProgress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).values_list('lecture_id', flat=True)
    
    next_lecture = Lecture.objects.filter(
        module__course=enrollment.course
    ).exclude(
        id__in=completed_lectures
    ).order_by('module__order', 'order').first()
    
    if next_lecture:
        return {
            'id': next_lecture.id,
            'title': next_lecture.title,
            'module': next_lecture.module.title
        }
    return None

def timesince(dt):
    from django.utils.timesince import timesince
    return timesince(dt)