from django.urls import path
from .views import trigger_report, get_report

urlpatterns = [
    path('trigger_report/', trigger_report, name='trigger_report'),
    path('get_report/<str:report_id>/', get_report, name='get_report'),
]