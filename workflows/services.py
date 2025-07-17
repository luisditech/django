# apps/workflows/services.py
from .models import Workflow

def list_workflows():
    """
    Returns a base queryset of all workflows, newest first.
    """
    return Workflow.objects.order_by('-created_at')
