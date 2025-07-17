# apps/workflows/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import WorkflowSerializer
from .services import list_workflows
from utils.pagination import paginate_queryset
from django.shortcuts import get_object_or_404
from .tasks import run_workflow

class WorkflowListView(APIView):
    """
    GET /api/workflows/?page=1&limit=10
    """
    @paginate_queryset(WorkflowSerializer)
    def get(self, request, *args, **kwargs):
        # return a dict with 'queryset' for the decorator
        return {'queryset': list_workflows()}


class WorkflowDetailView(APIView):
    """
    GET /api/workflows/<int:workflow_id>/
    """
    def get(self, request, workflow_id, *args, **kwargs):
        # grab your single workflow or 404
        wf = get_object_or_404(list_workflows(), id=workflow_id)
        # serialize it
        serializer = WorkflowSerializer(wf, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RunWorkflowView(APIView):
    def post(self, request, id):
        run_workflow.delay(id)
        return Response({"status": "success", "message": f"Workflow {id} is being executed"}, status=status.HTTP_202_ACCEPTED)