from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from .models import Workflow
from .tasks import run_workflow

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at", "run_button")
    search_fields = ("name",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:workflow_id>/run/",
                self.admin_site.admin_view(self.run_workflow_view),
                name="workflow-run",
            ),
        ]
        return custom_urls + urls

    def run_button(self, obj):
        url = reverse("admin:workflow-run", args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="background-color:#4CAF50; color:white; padding:5px 10px; border-radius:3px;">Run Workflow</a>',
            url,
        )
    run_button.short_description = "Run Workflow"
    run_button.allow_tags = True

    def run_workflow_view(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, pk=workflow_id)
        try:
            task = run_workflow.delay(workflow_id)
            messages.success(request, f"Workflow '{workflow.name}' triggered successfully (Task ID: {task.id}).")
        except Exception as e:
            messages.error(request, f"Error triggering workflow: {e}")
        return redirect(request.META.get("HTTP_REFERER", reverse("admin:workflows_workflow_changelist")))
