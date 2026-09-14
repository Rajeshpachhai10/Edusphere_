from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('dashboard/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('manage/<slug:slug>/', views.InstructorCourseManageView.as_view(), name='manage_course'),
    path('manage/<slug:slug>/add-module/', views.add_module, name='add_module'),
    path('manage/<slug:slug>/module/<int:module_id>/add-lesson/', views.add_lesson, name='add_lesson'),
    path('manage/<slug:slug>/module/<int:module_id>/edit/', views.edit_module, name='edit_module'),
    path('manage/<slug:slug>/lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('manage/<slug:slug>/toggle-publish/', views.toggle_publish, name='toggle_publish'),
]