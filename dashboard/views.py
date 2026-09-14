from django.contrib import messages
from django.db.models import Sum, Count
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView

from .mixins import AdminRequiredMixin
from accounts.models import CustomUser
from courses.models import Course
from payments.models import Order


class DashboardOverviewView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_students'] = CustomUser.objects.filter(role='student').count()
        context['total_instructors'] = CustomUser.objects.filter(role='instructor').count()
        context['total_courses'] = Course.objects.count()
        context['published_courses'] = Course.objects.filter(is_published=True).count()

        revenue_data = Order.objects.filter(status='completed').aggregate(total=Sum('total_amount'))
        context['total_revenue'] = revenue_data['total'] or 0

        context['pending_orders'] = Order.objects.filter(status='pending').count()
        context['completed_orders'] = Order.objects.filter(status='completed').count()
        return context


class CourseOversightView(AdminRequiredMixin, ListView):
    model = Course
    template_name = 'dashboard/course_oversight.html'
    context_object_name = 'courses'
    paginate_by = 15

    def get_queryset(self):
        queryset = Course.objects.select_related('instructor').annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-created_at')

        status = self.request.GET.get('status')
        if status == 'published':
            queryset = queryset.filter(is_published=True)
        elif status == 'unpublished':
            queryset = queryset.filter(is_published=False)

        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('q', '')
        return context


class UserManagementView(AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'dashboard/user_management.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = CustomUser.objects.exclude(role='admin').order_by('-created_at')

        role = self.request.GET.get('role')
        if role in ('student', 'instructor'):
            queryset = queryset.filter(role=role)

        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(email__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_role'] = self.request.GET.get('role', '')
        context['current_search'] = self.request.GET.get('q', '')
        return context


class ToggleUserActiveView(AdminRequiredMixin, View):
    def post(self, request, pk):
        target_user = get_object_or_404(CustomUser, pk=pk)

        if target_user.role == 'admin':
            messages.error(request, "Admin accounts cannot be managed from this dashboard.")
            return redirect('dashboard:user_management')

        if target_user.pk == request.user.pk:
            messages.error(request, "You cannot deactivate your own account.")
            return redirect('dashboard:user_management')

        target_user.is_active = not target_user.is_active
        target_user.save()

        status_word = "activated" if target_user.is_active else "deactivated"
        messages.success(request, f"{target_user.email} has been {status_word}.")
        return redirect('dashboard:user_management')


class PaymentOversightView(AdminRequiredMixin, ListView):
    model = Order
    template_name = 'dashboard/payment_oversight.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.select_related('student', 'course').order_by('-created_at')

        status = self.request.GET.get('status')
        if status in ('pending', 'completed', 'failed'):
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        return context


class MarkOrderFailedView(AdminRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.status != 'pending':
            messages.error(request, "Only pending orders can be manually marked as failed.")
            return redirect('dashboard:payment_oversight')

        order.mark_failed()
        messages.success(request, f"Order for {order.student.email} marked as failed.")
        return redirect('dashboard:payment_oversight')