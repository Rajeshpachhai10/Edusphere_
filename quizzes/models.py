from django.db import models
from django.conf import settings
from courses.models import Module


class Quiz(models.Model):
    module = models.OneToOneField(
        Module,
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(
        default=70,
        help_text="Minimum percentage required to pass"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['module']

    def __str__(self):
        return f"Quiz: {self.title} ({self.module.title})"

    def total_questions(self):
        return self.questions.count()


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text[:50]


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempted_at']

    def __str__(self):
        return f"{self.student.email} - {self.quiz.title} - {self.score}/{self.total_questions}"

    def score_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100)

    def grade(self):
        """
        Auto-grades this attempt by comparing each StudentAnswer
        to its question's correct choice. Sets score, total_questions,
        and passed, then saves.
        """
        answers = self.answers.select_related('question', 'selected_choice')
        correct_count = sum(1 for a in answers if a.is_correct)

        self.total_questions = self.quiz.total_questions()
        self.score = correct_count
        self.passed = self.score_percentage() >= self.quiz.passing_score
        self.save()


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')

    def save(self, *args, **kwargs):
        if self.selected_choice:
            self.is_correct = self.selected_choice.is_correct
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attempt.student.email} - {self.question.text[:30]}"