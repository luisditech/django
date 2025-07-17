import os
executed_flag = False

def register_workflow_tasks():
    global executed_flag
    if executed_flag or os.environ.get("RUN_MAIN") != "true":
        return
    executed_flag = True

    from django_celery_beat.models import PeriodicTask, IntervalSchedule
    from apps.workflows.models import Workflow
    import json
    import logging

    logger = logging.getLogger(__name__)
    schedule, _ = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.MINUTES)
    workflows = Workflow.objects.all()
    logger.info(f"🔄 Buscando workflows para crear tareas periódicas ({workflows.count()} encontrados)")

    for wf in workflows:
        task_name = f"workflow_{wf.id}_{wf.name.replace(' ', '_')}"
        if PeriodicTask.objects.filter(name=task_name).exists():
            logger.info(f"⏩ Tarea ya existe: {task_name}")
            continue
        PeriodicTask.objects.create(
            interval=schedule,
            name=task_name,
            task="run_workflow",
            args=json.dumps([wf.id]),
            enabled=False,
        )
        logger.info(f"✅ Tarea creada: {task_name}")
