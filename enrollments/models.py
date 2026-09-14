from django.db import models
from django.conf import settings
from courses.models import Course, Lesson


class Enrollment(models.Model):
    """
    Represents a student's enrollment in a course.
    One row = one student enrolled in one course, ever.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'},
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.email} → {self.course.title}"

    def progress_percentage(self):
        """
        Returns completion percentage (0-100) for this enrollment.
        Calculated live from LessonProgress rows rather than stored,
        so it's always accurate even if lessons are added/removed later.
        """
        total_lessons = Lesson.objects.filter(module__course=self.course).count()
        if total_lessons == 0:
            return 0
        completed_lessons = LessonProgress.objects.filter(
            student=self.student,
            lesson__module__course=self.course,
            completed=True
        ).count()
        return round((completed_lessons / total_lessons) * 100)
    
    
    def get_resume_lesson(self):
        """
        Determines which lesson the student should land on when clicking
        'Continue'. Returns the first incomplete lesson in course order,
        or the very first lesson if nothing's been completed yet, or the
        last lesson if everything is already done (review mode).
        """
        all_lessons = list(
            Lesson.objects.filter(module__course=self.course).order_by('module__order', 'order')
        )
        if not all_lessons:
            return None

        completed_lesson_ids = set(
            LessonProgress.objects.filter(
                student=self.student,
                lesson__module__course=self.course,
                completed=True
            ).values_list('lesson_id', flat=True)
        )

        for lesson in all_lessons:
            if lesson.id not in completed_lesson_ids:
                return lesson

        return all_lessons[-1]  # everything completed — land on the last lesson
    



class LessonProgress(models.Model):
    """
    Tracks whether a specific student has completed a specific lesson.
    Only created/updated once a student interacts with a lesson —
    no row means 'not started', not 'incomplete'.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        limit_choices_to={'role': 'student'},
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress_entries',
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.student.email} — {self.lesson.title}"

    def mark_complete(self):
        """
        Helper method to mark this lesson complete and stamp the time.
        Keeping this logic on the model (not scattered in the view) means
        any future code path that completes a lesson stays consistent.
        """
        from django.utils import timezone
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()