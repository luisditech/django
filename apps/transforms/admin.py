from django.contrib import admin
from .models import TransformationRule

@admin.register(TransformationRule)
class TransformationRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "get_type_display", "short_fields", "is_active", "created_at")
    list_filter = ("transform_type", "is_active")
    search_fields = ("name",)
    readonly_fields = ("created_at",)

    def short_fields(self, obj):
        fields = obj.config.get("fields", {})
        if isinstance(fields, dict):
            keys = list(fields.keys())
            display = ", ".join(keys[:3])
            return f"{display}..." if len(keys) > 3 else display
        return "-"
    short_fields.short_description = "Fields"

    def get_type_display(self, obj):
        return obj.transform_type
    get_type_display.short_description = "Type"
