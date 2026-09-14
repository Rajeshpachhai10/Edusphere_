from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, StudentAnswer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ['text', 'is_correct']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['text', 'order']
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'passing_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'module__title']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'order']
    list_filter = ['quiz']
    search_fields = ['text']
    inlines = [ChoiceInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'total_questions', 'passed', 'attempted_at']
    list_filter = ['passed', 'quiz', 'attempted_at']
    search_fields = ['student__email', 'quiz__title']
    readonly_fields = ['student', 'quiz', 'score', 'total_questions', 'passed', 'attempted_at']


admin.site.register(StudentAnswer)