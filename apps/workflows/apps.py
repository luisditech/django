from django.apps import AppConfig

class WorkflowsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.workflows'

    def ready(self):
        from django.db.utils import OperationalError
        import logging
        logger = logging.getLogger(__name__)

        try:
            from apps.workflows.tasks_register import register_workflow_tasks
            register_workflow_tasks()
            logger.info("✅ Tareas periódicas de workflows registradas.")
        except OperationalError:
            logger.warning("⚠️ Base de datos no disponible al registrar tareas periódicas.")
        except Exception as e:
            logger.exception(f"❌ Error registrando tareas periódicas: {e}")
