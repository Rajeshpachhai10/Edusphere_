from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Course, Module, Lesson, Category
from .forms import CourseForm, ModuleForm, LessonForm
from .mixins import InstructorRequiredMixin


class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9

    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True)
        category_slug = self.request.GET.get('category')
        query = self.request.GET.get('q')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_enrolled = False
        if user.is_authenticated and getattr(user, 'role', None) == 'student':
            from enrollments.models import Enrollment
            is_enrolled = Enrollment.objects.filter(
                student=user, course=self.object
            ).exists()
        context['is_enrolled'] = is_enrolled
        return context


class CourseCreateView(InstructorRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        messages.success(self.request, "Course created! Now add some modules.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('courses:manage_course', kwargs={'slug': self.object.slug})


class InstructorCourseManageView(InstructorRequiredMixin, DetailView):
    """The instructor's private view of their own course, for adding modules/lessons."""
    model = Course
    template_name = 'courses/manage_course.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


class InstructorDashboardView(InstructorRequiredMixin, ListView):
    """Lists all courses taught by the logged-in instructor, with manage links."""
    model = Course
    template_name = 'courses/instructor_dashboard.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


def add_module(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, "Module added.")
            return redirect('courses:manage_course', slug=slug)
    else:
        form = ModuleForm()
    return render(request, 'courses/module_form.html', {'form': form, 'course': course})


def add_lesson(request, slug, module_id):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, "Lesson added.")
            return redirect('courses:manage_course', slug=slug)
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form, 'course': course, 'module': module})


def edit_module(request, slug, module_id):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, "Module updated.")
            return redirect('courses:manage_course', slug=slug)
    else:
        form = ModuleForm(instance=module)
    return render(request, 'courses/module_form.html', {'form': form, 'course': course, 'editing': True})


def edit_lesson(request, slug, lesson_id):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated.")
            return redirect('courses:manage_course', slug=slug)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {'form': form, 'course': course, 'module': lesson.module, 'editing': True})


@login_required
@require_POST
def toggle_publish(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    course.is_published = not course.is_published
    course.save()
    status = "published" if course.is_published else "unpublished"
    messages.success(request, f"Course {status}.")
    return redirect('courses:manage_course', slug=slug)