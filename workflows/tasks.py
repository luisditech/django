import logging
from datetime import datetime
from celery import shared_task
from apps.works.models import Work
from apps.workflows.models import Workflow
from apps.workExecution.models import WorkExecution
from apps.workExecutionList.models import WorkExecutionList
from .run import run_single_work

logger = logging.getLogger(__name__)

@shared_task(name="run_workflow")
def run_workflow(workflow_id):
    if workflow_id is None:
        logger.warning("⚠️ No se proporcionó workflow_id a run_workflow")
        return {"status": "error", "message": "Missing workflow_id"}

    try:
        workflow = Workflow.objects.get(id=workflow_id)
        steps_raw = workflow.steps or []
        if not isinstance(steps_raw, list):
            logger.error(f"Workflow {workflow_id} tiene steps inválido: no es lista")
            return {"status": "error", "message": "Steps inválido"}

        steps_ids = []
        for step in steps_raw:
            if isinstance(step, dict) and "id" in step:
                logger.info(f"🧩 Lista de steps: {steps_ids}")
                steps_ids.append(step["id"])
            else:
                logger.warning(f"Paso inválido en workflow {workflow_id}: {step}")

        data = None  # Datos iniciales vacíos

        execution_list = WorkExecutionList.objects.create(
            workflow=workflow,
            total=len(steps_ids),
            status="processing",
            name=f"Workflow {workflow.name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        had_errors = False

        for idx, work_id in enumerate(steps_ids):
            logger.info(f"Ejecutando step {idx+1}/{len(steps_ids)} con work_id {work_id}")

            try:
                work = Work.objects.get(id=work_id)
                logger.info(f"Ejecutando work {work.id}: {work.name} ({work.operation_type})")

                data, work_execs = run_single_work(work, data)

                for exec_obj in work_execs:
                    execution_list.executions.add(exec_obj)
                    if exec_obj.status == "error":
                        had_errors = True
                        # logger.error(f"Work {work.id} terminó con error: {exec_obj.message}")

            except Work.DoesNotExist:
                had_errors = True
                msg = f"Work con id {work_id} no existe"
                logger.error(msg)
                error_exec = WorkExecution.objects.create(
                    work=None,
                    status="error",
                    message=msg
                )
                execution_list.executions.add(error_exec)

            except Exception as e:
                had_errors = True
                logger.error(f"Error ejecutando work {work_id}: {e}", exc_info=True)
                error_exec = WorkExecution.objects.create(
                    work_id=work_id,
                    status="error",
                    message=str(e)
                )
                execution_list.executions.add(error_exec)

        execution_list.status = "error" if had_errors else "success"
        execution_list.save()

        return {"status": "success" if not had_errors else "error"}
    
    except Exception as e:
        logger.error(f"[WORKFLOW ERROR] {str(e)}", exc_info=True)
        logger.exception("Workflow failed")
        WorkExecution.objects.create(
            work_id=None,
            status="error",
            message=str(e)
        )
        return {"status": "error", "message": str(e)}