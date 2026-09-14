from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<slug:course_slug>/', views.initiate_payment_view, name='initiate'),
    path('success/', views.payment_success_view, name='success'),
    path('failure/', views.payment_failure_view, name='failure'),
]

