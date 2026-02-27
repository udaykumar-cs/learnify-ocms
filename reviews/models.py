from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from courses.models import Course

class Review(models.Model):
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'student'],
                name='unique_student_course_review'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.email} - {self.course.title} - {self.rating}★"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update course average rating
        self.update_course_rating()

    def delete(self, *args, **kwargs):
        course = self.course
        super().delete(*args, **kwargs)
        # Update course average rating after deletion
        self.update_course_rating(course)

    def update_course_rating(self, course=None):
        if not course:
            course = self.course
        reviews = course.reviews.all()
        if reviews.exists():
            avg_rating = sum(r.rating for r in reviews) / reviews.count()
            course.average_rating = round(avg_rating, 2)
            course.total_reviews = reviews.count()
        else:
            course.average_rating = 0
            course.total_reviews = 0
        course.save(update_fields=['average_rating', 'total_reviews'])