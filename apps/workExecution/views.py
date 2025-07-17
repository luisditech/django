# apps/workExecution/api_views.py

from functools import wraps
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import WorkExecution
from .serializers import WorkExecutionSerializer
from utils.pagination import paginate_queryset  # wherever you put your decorator

class WorkExecutionDetailAPIView(APIView):
    """
    GET /api/workexecutions/{pk}/
    """
    def get(self, request, pk, *args, **kwargs):
        try:
            exec = WorkExecution.objects.get(pk=pk)
        except WorkExecution.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        data = WorkExecutionSerializer(exec, context={"request": request}).data
        return Response(data)


class WorkExecutionListAPIView(APIView):
    """
    GET /api/workexecutions/?page=1&limit=10
    """
    @paginate_queryset(WorkExecutionSerializer)
    def get(self, request, *args, **kwargs):
        qs = WorkExecution.objects.all().order_by("-started_at")
        return {"queryset": qs}