# apps/workflows/serializers.py

from rest_framework import serializers
from django_celery_beat.models import PeriodicTask
from .models import Workflow

class WorkflowSerializer(serializers.ModelSerializer):
    periodic_task = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = (
            "id",
            "name",
            "description",
            "steps",
            "created_at",
            "updated_at",
            "periodic_task",
        )

    def get_periodic_task(self, obj):
        """
        Look for a PeriodicTask named workflow_<id>_<name> and return
        its enabled state, schedule string, last run, and total runs.
        """
        prefix = f"workflow_{obj.id}_"
        # pick the first matching periodic task (if any), avoid exceptions on multiple matches
        task = PeriodicTask.objects.filter(name__startswith=prefix).first()
        if not task:
            return None

        # assemble a human‐readable schedule
        if task.interval:
            every = task.interval.every
            unit = task.interval.get_period_display().lower()
            schedule = f"every {every} {unit}"
        elif task.crontab:
            c = task.crontab
            schedule = f"{c.minute} {c.hour} {c.day_of_month} {c.month_of_year} {c.day_of_week}"
        else:
            schedule = None

        return {
            "name":           task.name,
            "enabled":        task.enabled,
            "schedule":       schedule,
            "last_run_at":    task.last_run_at,
            "total_run_count": task.total_run_count,
        }
