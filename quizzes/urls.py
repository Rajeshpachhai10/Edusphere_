from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('module/<int:module_id>/', views.quiz_detail_view, name='quiz_detail'),
    path('module/<int:module_id>/create/', views.create_quiz_view, name='create_quiz'),
    path('module/<int:module_id>/manage/', views.manage_quiz_view, name='manage_quiz'),
    path('module/<int:module_id>/add-question/', views.add_question_view, name='add_question'),
    path('module/<int:module_id>/submit/', views.submit_quiz_view, name='submit_quiz'),
    path('attempt/<int:attempt_id>/result/', views.quiz_result_view, name='quiz_result'),
]