from django.contrib import admin
from .models import Work

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "operation_type",
        "connection",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("operation_type", "is_active")
    search_fields = ("name", "connection__name")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("homologations", "transformations")  # para ManyToMany campos

    fieldsets = (
        (None, {
            "fields": (
                "name",
                "operation_type",
                "connection",
                "config",
                "mapping",
                "homologations",
                "transformations",
                "is_active",
            )
        }),
        ("Tiempos", {
            "fields": ("created_at", "updated_at"),
        }),
    )
