from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardOverviewView.as_view(), name='overview'),
    path('courses/', views.CourseOversightView.as_view(), name='course_oversight'),
    path('users/', views.UserManagementView.as_view(), name='user_management'),
    path('users/<int:pk>/toggle-active/', views.ToggleUserActiveView.as_view(), name='toggle_user_active'),
    path('payments/', views.PaymentOversightView.as_view(), name='payment_oversight'),
    path('payments/<int:pk>/mark-failed/', views.MarkOrderFailedView.as_view(), name='mark_order_failed'),
]