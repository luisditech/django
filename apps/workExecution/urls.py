from django.urls import path
from .views import WorkExecutionListAPIView, WorkExecutionDetailAPIView

urlpatterns = [
    path('workexecutions/', WorkExecutionListAPIView.as_view(), name='workexecution-list'),
    path('workexecutions/<int:pk>/', WorkExecutionDetailAPIView.as_view(), name='workexecution-detail'),
]