from django.db import models

TRANSFORM_TYPES = [
    ("set", "Set (establece campos nuevos o sobrescribe existentes)"),
    ("put", "Put (agrega en listas o crea estructuras si no existen)"),
    ("delete", "Delete (elimina campos)"),
]
class TransformationRule(models.Model):
    name = models.CharField(max_length=100, unique=True)
    transform_type = models.CharField(
        max_length=20,
        choices=TRANSFORM_TYPES,
        help_text="Tipo de transformación: set, put o delete"
    )
    config = models.JSONField(help_text="Configuración: {'fields': {'field.path': value}}")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.transform_type})"

    def get_config(self):
        return {
            "type": self.transform_type,
            **self.config
        }