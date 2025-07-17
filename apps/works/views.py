# apps/works/api_views.py

import json
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Work
from .serializers import WorkSerializer
from .operation_runner import run_operation
from utils.pagination import paginate_queryset

logger = logging.getLogger(__name__)

class WorkListCreateAPIView(APIView):
    """
    GET  /api/operations/?page=1&limit=10   → paginated list of works
    POST /api/operations/                  → create a new Work
    """
    @paginate_queryset(WorkSerializer)
    def get(self, request, *args, **kwargs):
        return {'queryset': Work.objects.all()}

    def post(self, request, *args, **kwargs):
        serializer = WorkSerializer(data=request.data)
        if serializer.is_valid():
            work = serializer.save()
            return Response(WorkSerializer(work).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkDetailAPIView(APIView):
    """
    GET    /api/operations/{pk}/      → retrieve
    PUT    /api/operations/{pk}/      → update
    DELETE /api/operations/{pk}/      → delete
    """
    def get_object(self, pk):
        try:
            return Work.objects.get(pk=pk)
        except Work.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        work = self.get_object(pk)
        if not work:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(WorkSerializer(work).data)

    def put(self, request, pk, *args, **kwargs):
        work = self.get_object(pk)
        if not work:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = WorkSerializer(work, data=request.data)
        if serializer.is_valid():
            work = serializer.save()
            return Response(WorkSerializer(work).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        work = self.get_object(pk)
        if not work:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        work.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkRunAPIView(APIView):
    """
    POST /api/operations/{pk}/run/  → triggers run_operation for that Work
    """
    def post(self, request, pk, *args, **kwargs):
        try:
            work = Work.objects.get(pk=pk)
        except Work.DoesNotExist:
            return Response({"error": "Work not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            result = run_operation(work)
            return Response(result)
        except Exception as e:
            logger.exception(f"Error running work {pk}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
