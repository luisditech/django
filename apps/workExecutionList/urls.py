from django.urls import path
from .views import (
    WorkExecutionListListAPIView,
    WorkExecutionListByWorkflowAPIView,
    WorkExecutionListExecutionsAPIView
)

urlpatterns = [
    path(
        "workexecutionlists/",
        WorkExecutionListListAPIView.as_view(),
        name="workexecutionlist-list"
    ),
    path(
        'workexecutionlists/workflow/<int:workflow_id>/',
        WorkExecutionListByWorkflowAPIView.as_view(),
        name="workexecutionlist-detail"
    ),
    path('workexecutionlists/<int:pk>/', WorkExecutionListExecutionsAPIView.as_view(),
         name='workexecutionlist-detail'),
]
