from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

from courses.models import Course, Lesson
from .models import Enrollment, LessonProgress


@login_required
@require_POST
def enroll_view(request, slug):
    """
    Enrolls the logged-in student in a course.
    POST-only (like toggle_publish in Phase 2) because enrolling changes
    state — it should never happen from a GET link/bookmark/crawler visit.
    """
    course = get_object_or_404(Course, slug=slug, is_published=True)

    if request.user.role != 'student':
        messages.error(request, "Only student accounts can enroll in courses.")
        return redirect('courses:course_detail', slug=slug)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    if created:
        messages.success(request, f"You're enrolled in {course.title}! Let's start learning.")
    else:
        messages.info(request, "You're already enrolled in this course.")

    return redirect('courses:course_detail', slug=slug)


@login_required
def lesson_detail_view(request, slug, lesson_id):
    """
    Shows a single lesson's content — but ONLY if the requesting student
    is enrolled in the course that lesson belongs to.
    """
    course = get_object_or_404(Course, slug=slug, is_published=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)

    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course
    ).exists()

    if not is_enrolled:
        messages.warning(request, "You need to enroll in this course to view lesson content.")
        return redirect('courses:course_detail', slug=slug)

    progress, _ = LessonProgress.objects.get_or_create(
        student=request.user, lesson=lesson
    )

    # Build ordered lesson list for prev/next navigation within the course
    all_lessons = list(
        Lesson.objects.filter(module__course=course).order_by('module__order', 'order')
    )
    current_index = all_lessons.index(lesson)
    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None

    context = {
        'course': course,
        'lesson': lesson,
        'progress': progress,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    }
    return render(request, 'enrollments/lesson_detail.html', context)


@login_required
@require_POST
def mark_lesson_complete(request, lesson_id):
    """
    Marks a lesson as completed for the logged-in student.
    Ownership/enrollment is re-verified here — never trust that a POST
    only comes from a student who legitimately reached this lesson via
    the enrolled flow above.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.module.course

    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course
    ).exists()
    if not is_enrolled:
        messages.error(request, "You must be enrolled to update progress.")
        return redirect('courses:course_detail', slug=course.slug)

    progress, _ = LessonProgress.objects.get_or_create(
        student=request.user, lesson=lesson
    )
    progress.mark_complete()
    messages.success(request, f"Marked \"{lesson.title}\" as complete.")

    return redirect('enrollments:lesson_detail', slug=course.slug, lesson_id=lesson.id)


@login_required
def my_courses_view(request):
    """
    Student dashboard: lists all courses the student is enrolled in,
    with progress bars.
    """
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    return render(request, 'enrollments/my_courses.html', {'enrollments': enrollments})


@login_required
def continue_course_view(request, slug):
    """
    Computes where this student should land based on progress, and
    redirects straight there — skips the course marketing page entirely
    for already-enrolled students.
    """
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)

    resume_lesson = enrollment.get_resume_lesson()
    if resume_lesson is None:
        messages.info(request, "This course doesn't have any lessons yet.")
        return redirect('courses:course_detail', slug=slug)

    return redirect('enrollments:lesson_detail', slug=course.slug, lesson_id=resume_lesson.id)