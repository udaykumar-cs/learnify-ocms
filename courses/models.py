from django.db import models
from django.conf import settings

# http://127.0.0.1:8000/api/token/
# http://127.0.0.1:8000/api/

# http://127.0.0.1:8000/api/progress/

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class Course(models.Model):

    class Level(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    level = models.CharField(max_length=20, choices=Level.choices)

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="courses"
    )

    is_published = models.BooleanField(default=False)

    # Performance Optimization Fields
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['instructor']),
            models.Index(fields=['level']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return self.title
    

class Module(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules"
    )

    title = models.CharField(max_length=255)

    order = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'order'],
                name='unique_module_order_per_course'
            )
        ]
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"
    

class Lecture(models.Model):

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lectures"
    )

    title = models.CharField(max_length=255)

    video_url = models.URLField()
    notes = models.TextField(blank=True)

    order = models.PositiveIntegerField()

    duration = models.PositiveIntegerField(help_text="Duration in seconds")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['module', 'order'],
                name='unique_lecture_order_per_module'
            )
        ]
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"