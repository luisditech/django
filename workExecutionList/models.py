from django.db import models
from apps.workflows.models import Workflow
from apps.workExecution.models import WorkExecution

class WorkExecutionList(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, null=True)
    total = models.PositiveIntegerField(null=True)
    name = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=50, null=True)
    executions = models.ManyToManyField(
        WorkExecution,
        related_name="execution_lists",
    )
    created_at = models.DateTimeField(auto_now_add=True)
