from django.urls import path
from . import views

app_name = 'forums'

urlpatterns = [
    path('course/<slug:course_slug>/', views.thread_list_view, name='thread_list'),
    path('course/<slug:course_slug>/new/', views.create_thread_view, name='create_thread'),
    path('thread/<int:thread_id>/', views.thread_detail_view, name='thread_detail'),
    path('thread/<int:thread_id>/reply/', views.reply_view, name='reply'),
]