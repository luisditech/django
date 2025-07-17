from django.db import models
from apps.works.models import Work  

class WorkExecution(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="executions")
    status = models.CharField(max_length=20, choices=[
        ("success", "Success"),
        ("error", "Error")
    ])
    message = models.TextField(blank=True, null=True)
    request = models.TextField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.work.name} - {self.status} - {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
