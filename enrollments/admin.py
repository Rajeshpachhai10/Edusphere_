from django.contrib import admin
from .models import Enrollment, LessonProgress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'progress_display')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('student__email', 'course__title')

    def progress_display(self, obj):
        return f"{obj.progress_percentage()}%"
    progress_display.short_description = 'Progress'


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed',)
    search_fields = ('student__email', 'lesson__title')