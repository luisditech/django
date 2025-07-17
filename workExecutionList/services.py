from django.db.models import Count, Q
from .models import WorkExecutionList

def list_work_execution_lists():
    return (
        WorkExecutionList.objects
        .annotate(
            exec_count=Count(
                "executions",
                filter=Q(executions__request__isnull=False) & ~Q(executions__request=""),
            )
        )
        .order_by("-created_at")
    )

