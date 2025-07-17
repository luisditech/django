from rest_framework import serializers
from apps.workExecution.models import WorkExecution
from .models import WorkExecutionList

class WorkExecutionListSummarySerializer(serializers.ModelSerializer):
    # total se toma de exec_count anotado en el queryset
    total = serializers.IntegerField(source="exec_count", read_only=True)

    class Meta:
        model = WorkExecutionList
        fields = [
            "id",
            "workflow",
            "total",
            "name",
            "status",
            "created_at",
        ]
        read_only_fields = ("id", "created_at")
        
class WorkExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExecution
        fields = ("id", "status", "message", "request", "response", "started_at")

class WorkExecutionListSerializer(serializers.ModelSerializer):
    executions = WorkExecutionSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = WorkExecutionList
        fields = [
            "id",
            "workflow",
            "total",
            "name",
            "status",
            "created_at",
            "executions",
        ]
        read_only_fields = ("id", "created_at")

    def get_total(self, obj):
        """
        Devuelve la cantidad de ejecuciones asociadas que tienen un campo "request" no vacío.
        """
        return obj.executions.filter(request__isnull=False).exclude(request__exact="").count()

class WorkExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExecution
        fields = ("id", "status", "message", "request", "response", "started_at")