from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from courses.models import Course
from enrollments.models import Enrollment
from .models import Thread, Post


def _user_has_course_access(user, course):
    """
    A student needs to be enrolled. An instructor needs to be
    the one teaching this specific course. Anyone else is blocked.
    """
    if user.role == 'student':
        return Enrollment.objects.filter(student=user, course=course).exists()
    if user.role == 'instructor':
        return course.instructor_id == user.id
    return False


@login_required
def thread_list_view(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    if not _user_has_course_access(request.user, course):
        messages.error(request, "You don't have access to this course's discussions.")
        return redirect('courses:course_detail', slug=course.slug)

    threads = course.threads.select_related('author')

    context = {'course': course, 'threads': threads}
    return render(request, 'forums/thread_list.html', context)


@login_required
def create_thread_view(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    if not _user_has_course_access(request.user, course):
        messages.error(request, "You don't have access to this course's discussions.")
        return redirect('courses:course_detail', slug=course.slug)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()

        if title and body:
            thread = Thread.objects.create(
                course=course,
                author=request.user,
                title=title,
                body=body
            )
            return redirect('forums:thread_detail', thread_id=thread.id)
        else:
            messages.error(request, "Both a title and a question are required.")

    context = {'course': course}
    return render(request, 'forums/create_thread.html', context)


@login_required
def thread_detail_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    if not _user_has_course_access(request.user, thread.course):
        messages.error(request, "You don't have access to this course's discussions.")
        return redirect('courses:course_detail', slug=thread.course.slug)

    posts = thread.posts.select_related('author')

    context = {'thread': thread, 'posts': posts}
    return render(request, 'forums/thread_detail.html', context)


@login_required
@require_POST
def reply_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    # Re-verify access here too — same reasoning as mark_lesson_complete
    # and submit_quiz_view: never trust that this request only arrived
    # via the thread_detail page's own reply form.
    if not _user_has_course_access(request.user, thread.course):
        messages.error(request, "You don't have access to this course's discussions.")
        return redirect('courses:course_detail', slug=thread.course.slug)

    body = request.POST.get('body', '').strip()
    if body:
        Post.objects.create(thread=thread, author=request.user, body=body)
    else:
        messages.error(request, "Reply can't be empty.")

    return redirect('forums:thread_detail', thread_id=thread.id)