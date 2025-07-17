# apps/workExecution/serializers.py

from rest_framework import serializers
from .models import WorkExecution

class WorkExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExecution
        fields = [
            "id",
            "work",
            "status",
            "message",
            "request",
            "response",
            "started_at",
        ]
        read_only_fields = fields