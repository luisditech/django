from django.db import models

class Workflow(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    # Guardamos la lista ordenada de steps aquí, con toda la configuración de cada paso
    steps = models.JSONField(default=list, blank=True, help_text="Lista ordenada de pasos con configuración")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name