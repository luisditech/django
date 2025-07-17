from django.db import models
from django.contrib.postgres.fields import JSONField

class HomologationRule(models.Model):
    name = models.CharField(max_length=100)
    csv_file = models.FileField(upload_to='homologations/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name