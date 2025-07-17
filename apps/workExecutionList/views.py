# apps/workExecution/api_views.py
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import WorkExecutionList
from .serializers import WorkExecutionSerializer,WorkExecutionListSummarySerializer
from .services import list_work_execution_lists
from utils.pagination import paginate_queryset

class WorkExecutionListListAPIView(APIView):
    """
    GET /api/workexecutionlists/?page=1&limit=10
    Devuelve todas las WorkExecutionList paginadas SIN el array `executions`.
    """
    @paginate_queryset(WorkExecutionListSummarySerializer)
    def get(self, request, *args, **kwargs):
        return {"queryset": list_work_execution_lists()}
    



class WorkExecutionListByWorkflowAPIView(APIView):
    """
    GET /api/workexecutionlists/workflow/{workflow_id}/
    Devuelve todas las WorkExecutionList asociadas al workflow dado, paginadas,
    SIN el array `executions` (pero con total calculado).
    """
    @paginate_queryset(WorkExecutionListSummarySerializer)
    def get(self, request, workflow_id, *args, **kwargs):
        qs = (
            WorkExecutionList.objects
            .filter(workflow_id=workflow_id)
            .annotate(exec_count=Count('executions'))
            .order_by('-created_at')
        )
        if not qs.exists():
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return {"queryset": qs}


class WorkExecutionListExecutionsAPIView(APIView):
    """
    GET /api/workexecutionlists/{pk}/executions/?page=1&limit=10
    Devuelve las ejecuciones de una WorkExecutionList, paginadas.
    """
    @paginate_queryset(WorkExecutionSerializer)
    def get(self, request, pk, *args, **kwargs):
        try:
            wel = WorkExecutionList.objects.get(pk=pk)
        except WorkExecutionList.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        qs = wel.executions.order_by("-started_at")
        return {"queryset": qs}