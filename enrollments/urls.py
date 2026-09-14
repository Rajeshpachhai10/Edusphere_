from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('enroll/<slug:slug>/', views.enroll_view, name='enroll'),
    path('my-courses/', views.my_courses_view, name='my_courses'),
    path('lesson/<slug:slug>/<int:lesson_id>/', views.lesson_detail_view, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_complete'),
    path('continue/<slug:slug>/', views.continue_course_view, name='continue_course'),
]
