# apps/workflows/urls.py
from django.urls import path
from .views import WorkflowListView, WorkflowDetailView, RunWorkflowView

urlpatterns = [
    path('api/workflows/', WorkflowListView.as_view(), name='workflow-list'),
    path('api/workflows/<int:workflow_id>/', WorkflowDetailView.as_view(), name='workflow-detail'),
    path('api/workflow/run/<int:id>/', RunWorkflowView.as_view(), name='run-workflow'),
]