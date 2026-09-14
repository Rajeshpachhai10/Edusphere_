from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import StudentSignUpForm, InstructorSignUpForm, EmailAuthenticationForm


def register_choice(request):
    return render(request, 'accounts/register_choice.html')


def student_register(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to EduSphere, {user.first_name}! Your student account is ready.")
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = StudentSignUpForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'Student'})


def instructor_register(request):
    if request.method == 'POST':
        form = InstructorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to EduSphere, {user.first_name}! Your instructor account is ready.")
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = InstructorSignUpForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'Instructor'})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().first_name}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid email or password. Please try again.")
        return super().form_invalid(form)


def user_logout(request):
    logout(request)
    messages.success(request, "You've been logged out successfully.")
    return redirect('home')