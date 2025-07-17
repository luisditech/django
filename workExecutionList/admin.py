from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.db import models
from .models import WorkExecutionList

@admin.register(WorkExecutionList)
class WorkExecutionListAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "execution_count")
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Solo contar, no traer ejecuciones completas
        qs = qs.annotate(_execution_count=models.Count("executions"))
        return qs

    def execution_count(self, obj):
        return getattr(obj, "_execution_count", 0)
    execution_count.short_description = "Executions"