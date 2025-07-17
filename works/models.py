from django.db import models
from apps.connections.models import Connection
from apps.homologations.models import HomologationRule
from apps.transforms.models import TransformationRule

class Work(models.Model):
    OPERATION_TYPES = (
        ("origin", "Origin (Data Source)"),
        ("destiny", "Destiny (Data Target)"),
        ("transfer", "Transfer"),
        ("data", "Data")
    )
    name = models.CharField(max_length=255, unique=True)
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPES)
    connection = models.ForeignKey(
        Connection,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    config = models.JSONField(blank=True, null=True)
    mapping = models.JSONField(blank=True, null=True)
    homologations = models.ManyToManyField(HomologationRule, blank=True, related_name='works')
    transformations = models.ManyToManyField(TransformationRule, blank=True, related_name='works')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.operation_type})"