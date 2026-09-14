from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

from courses.models import Module
from enrollments.models import Enrollment
from .models import Quiz, Question, QuizAttempt, StudentAnswer, Choice
from .forms import QuizForm, QuestionForm, ChoiceFormSet


def _get_quiz_or_404(module_id):
    module = get_object_or_404(Module, id=module_id)
    quiz = get_object_or_404(Quiz, module=module)
    return module, quiz


def _student_is_enrolled(user, module):
    return Enrollment.objects.filter(
        student=user,
        course=module.course
    ).exists()


@login_required
def quiz_detail_view(request, module_id):
    module, quiz = _get_quiz_or_404(module_id)

    if not _student_is_enrolled(request.user, module):
        messages.error(request, "You must be enrolled in this course to take the quiz.")
        return redirect('courses:course_detail', slug=module.course.slug)

    questions = quiz.questions.prefetch_related('choices').all()

    context = {
        'quiz': quiz,
        'module': module,
        'questions': questions,
    }
    return render(request, 'quizzes/quiz_detail.html', context)


@login_required
@require_POST
def submit_quiz_view(request, module_id):
    module, quiz = _get_quiz_or_404(module_id)

    if not _student_is_enrolled(request.user, module):
        messages.error(request, "You must be enrolled in this course to submit this quiz.")
        return redirect('courses:course_detail', slug=module.course.slug)

    questions = quiz.questions.all()

    with transaction.atomic():
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz
        )

        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            selected_choice = None
            if choice_id:
                selected_choice = Choice.objects.filter(
                    id=choice_id,
                    question=question
                ).first()

            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=selected_choice
            )

        attempt.grade()

    return redirect('quizzes:quiz_result', attempt_id=attempt.id)


@login_required
def quiz_result_view(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        student=request.user
    )

    context = {'attempt': attempt}
    return render(request, 'quizzes/quiz_result.html', context)


@login_required
def create_quiz_view(request, module_id):
    module = get_object_or_404(Module, id=module_id, course__instructor=request.user)

    if hasattr(module, 'quiz'):
        messages.info(request, "This module already has a quiz.")
        return redirect('courses:manage_course', slug=module.course.slug)

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.module = module
            quiz.save()
            messages.success(request, f"Quiz '{quiz.title}' created. Now add its questions.")
            return redirect('quizzes:manage_quiz', module_id=module.id)
    else:
        form = QuizForm()

    context = {'form': form, 'module': module}
    return render(request, 'quizzes/create_quiz.html', context)


@login_required
def manage_quiz_view(request, module_id):
    module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
    quiz = get_object_or_404(Quiz, module=module)
    questions = quiz.questions.prefetch_related('choices').all()

    context = {'module': module, 'quiz': quiz, 'questions': questions}
    return render(request, 'quizzes/manage_quiz.html', context)


@login_required
def add_question_view(request, module_id):
    module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
    quiz = get_object_or_404(Quiz, module=module)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        question = Question(quiz=quiz)

        if form.is_valid():
            question.text = form.cleaned_data['text']
            question.order = form.cleaned_data['order']

        formset = ChoiceFormSet(request.POST, instance=question)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                question.save()
                formset.save()
            messages.success(request, "Question added.")
            return redirect('quizzes:manage_quiz', module_id=module.id)
    else:
        form = QuestionForm()
        formset = ChoiceFormSet(instance=Question(quiz=quiz))

    context = {'form': form, 'formset': formset, 'quiz': quiz, 'module': module}
    return render(request, 'quizzes/add_question.html', context)