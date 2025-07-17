from .models import WorkExecution

def list_executions():
    # return all executions, newest first
    return WorkExecution.objects.all().order_by('-started_at')

def get_execution(execution_id):
    return WorkExecution.objects.get(pk=execution_id)