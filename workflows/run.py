import os
import io
import csv
import json
import logging
import random
from io import BytesIO
from datetime import datetime
from collections import OrderedDict

from apps.works.models import Work
from apps.workExecution.models import WorkExecution
from apps.connections.services import (
    http_request_data,
    read_from_ftp_or_sftp,
    write_to_ftp_or_sftp,
    select_from_postgres,
    insert_into_postgres,
    insert_into_fallback_table,
    normalize_payload,
    apply_mapping_to_dataset,
    send_to_netsuite,
    get_nested_value,
    match_conditions
)
from apps.transforms.apply import apply_transformation_rules
from apps.homologations.services import (
    load_homologation_dict,
    apply_homologation_to_properties
)

from .utils import map_payload
from .utils import evaluate_branching
from ..connections.models import Connection

logger = logging.getLogger(__name__)


def run_single_work(work: Work, input_data):
    global data
    conn = work.connection
    conf = work.config or {}
    logger.info(input_data)
    # --- Conditional redirect logic ---
    if_conditional = conf.get("if")
    if isinstance(if_conditional, dict):
        alt_work_id = if_conditional.get("work")
        conditions = if_conditional.get("conditions", [])
        if alt_work_id and conditions:
            if isinstance(input_data, dict):
                if match_conditions(input_data, conditions):
                    logger.info(f"🔁 Redirigiendo ejecución de Work {work.id} a Work {alt_work_id} por condiciones avanzadas")
                    from apps.works.models import Work as WorkModel
                    alt_work = WorkModel.objects.get(id=alt_work_id)
                    return run_single_work(alt_work, input_data)
            elif isinstance(input_data, list):
                logger.info(f"Evaluando {len(input_data)} entradas para redirección condicional")
                executions = []
                redirected_data = []
                for i, entry in enumerate(input_data):
                    if match_conditions(entry, conditions):
                        logger.info(f"🔁 Entrada #{i} cumple condiciones, redirigiendo a Work {alt_work_id}")
                        from apps.works.models import Work as WorkModel
                        alt_work = WorkModel.objects.get(id=alt_work_id)
                        result_data, execs = run_single_work(alt_work, entry)
                        executions.extend(execs)
                        redirected_data.extend(result_data if isinstance(result_data, list) else [result_data])
                    else:
                        logger.info(f"⏩ Entrada #{i} no cumple condiciones, se mantiene igual")
                        redirected_data.append(entry)
                input_data = redirected_data
    mapping = work.mapping or {}
    origin_type = conn.type.lower() if conn else None
    operation_type = work.operation_type.lower() if work else None
    condition = conf.get("condition")
    executions = []

    try:
        # --- Obtener datos ---
        if input_data is None and operation_type == 'origin':
            if origin_type in ["rest", "graphql", "shopify"]:
                method = conf.get("method", "get").lower()
                payload = input_data
                path = conf.get("path")
                data = http_request_data(conn, conf, method=method, data=payload, path_override=path)

            elif origin_type == "postgresql":
                table = conf.get("table")
                if not table:
                    raise ValueError("Missing 'table' in PostgreSQL config.")
                where = conf.get("where_clause")
                params = conf.get("params")
                query = conf.get("query")
                data = select_from_postgres(conn, table, where_clause=where, params=params, queryParams=query)

            elif origin_type == "sftp":
                file_buffer = read_from_ftp_or_sftp(conn, conf)

                if isinstance(file_buffer, BytesIO):
                    file_buffer = file_buffer.read().decode("utf-8-sig")
                    file_buffer = file_buffer.lstrip("\ufeff")

                # Determine how to parse the incoming file_buffer: JSON first, then CSV
                try:
                    # Try JSON
                    data = json.loads(file_buffer)
                except json.JSONDecodeError:
                    # Remove UTF-8 BOM if present
                    file_buffer = file_buffer.lstrip("\ufeff")
                    # Fallback to CSV: try comma then semicolon
                    for delim in (",", ";"):
                        try:
                            reader = csv.DictReader(io.StringIO(file_buffer), delimiter=delim)
                            data = list(reader)
                            break
                        except Exception:
                            continue
                    else:
                        raise ValueError("Unsupported file format: not JSON or CSV")

            elif origin_type is None:
                data = []

            else:
                raise ValueError(f"Unsupported connection type: {origin_type}")

            executions.append(WorkExecution.objects.create(
                work=work,
                status="success",
                message="Datos obtenidos correctamente",
                response=json.dumps(data)[:2000],
            ))
        else:
            data = input_data

        # --- Normalizar ---
        source = conf.get('source') or None
        if data:
            data = normalize_payload(data)

        # --- Mapping ---
        if source:
            data = data[0].get(source)
        #if mapping:
        #    data = apply_mapping_to_dataset(data, mapping)
        #    executions.append(WorkExecution.objects.create(
        #        work=work,
        #        status="success",
        #       message="Mapping aplicado correctamente",
        #        response=json.dumps(data)[:2000],
        #    ))
        if condition and condition["job"] and condition["job"] == "validate_send_to_finecom_sprint":
            for input_object in input_data:
                payloads = input_object.get("payload")
                if isinstance(payloads, list):
                    for payload in payloads:
                        ext_work_id = evaluate_branching(conf, payload)
                        next_work = Work.objects.get(id=ext_work_id)
                        bd_connection = Connection.objects.get(name="postgres_db")
                        next_work_mapping = next_work.mapping or {}
                        next_work_conf = next_work.config or {}
                        next_work_conn = next_work.connection
                        # Map data
                        payload_mapped = map_payload(next_work_mapping, payload)
                        random_number = f"SO-{random.randint(0, 10000):05}-TP"
                        delivery_number = f"D{random.randint(0, 10000):05}-TP"
                        if "sprint" not in next_work_conn.config.get("base_url", "").lower():
                            payload_mapped[0]["DeliveryNumber"] = delivery_number
                            payload_mapped[0]["OrderNumber"] = random_number
                        else:
                            sprint_order_number = f"{random.randint(0, 10000):05}"
                            payload_mapped[0]["CustomerRef1"] = int(sprint_order_number)
                            payload_mapped[0]["SalesOrderId"] = int(sprint_order_number)
                            payload_mapped[0]["CustomerRef2"] = f"#{sprint_order_number}"
                        method = next_work_conf.get("method", "get").lower()
                        path = next_work_conf.get("path")
                        try:
                            data_to_persist = {}
                            order_created = http_request_data(next_work_conn, next_work_conf, method=method, data=payload_mapped[0], path_override=path)
                            table = "orchestrator_data"
                            now = datetime.now().isoformat()
                            order_created["status"] = "SEND_TO_SPRINT" if "sprint" in next_work_conn.config.get("base_url", "").lower() else "SEND_TO_FINECOM"
                            data_to_persist["operation_id"] = ext_work_id
                            data_to_persist["payload"] = order_created
                            data_to_persist["ingested_at"] = now
                            insert_into_postgres(bd_connection, table, data_to_persist)
                        except Exception as e:
                            continue
            executions.append(WorkExecution.objects.create(
                work=work,
                status="success",
                message="Datos procesados exitosamente",
                response=json.dumps(input_object.get("payload"))[:2000],
            ))

        if condition and condition["job"] and condition["job"] == "validate_fulfillment_finecom_sprint":
            for input_object in input_data:
                payload = input_object.get("payload")
                try:
                    if payload["status"] and "SEND_TO" in payload["status"]:
                        next_work_id_if_true = conf["if_true"]["next_work"]
                        next_work_id_if_false = conf["if_false"]["next_work"]
                        value_condition = condition["value"][0]
                        payload_status = payload["status"]
                        ext_work_id = next_work_id_if_true if payload_status == value_condition else next_work_id_if_false
                        next_work = Work.objects.get(id=ext_work_id)
                        next_work_conf = next_work.config or {}
                        next_work_conn = next_work.connection
                        method = next_work_conf.get("method", "get").lower()
                        path = next_work_conf.get("path")
                        if '-orderid-' in path:
                            path = path.replace("-orderid-", payload["OrderNumber"])
                        sadasd = "asdasd"
                        data = http_request_data(next_work_conn, next_work_conf, method=method, data=None, path_override=path)
                except Exception as e:
                    continue
            executions.append(WorkExecution.objects.create(
                work=work,
                status="success",
                message="Fulfillments procesados exitosamente",
                response=json.dumps(input_object.get("payload"))[:2000],
            ))

        # --- Homologaciones ---
        property_map = conf.get("property_map", {})
        if property_map and work.homologations.exists():
            first_h = work.homologations.first()
            csv_path = first_h.csv_file.path if hasattr(first_h.csv_file, 'path') else first_h.csv_file

            homologation_dict = load_homologation_dict(csv_path)

            data = apply_homologation_to_properties(data, homologation_dict, property_map)

            executions.append(WorkExecution.objects.create(
                work=work,
                status="success",
                message="Homologaciones aplicadas correctamente",
                response=json.dumps(data[:1]),
            ))

        # --- Transformaciones ---
        transformation_rules = list(work.transformations.filter(is_active=True))
        if transformation_rules:
            data = apply_transformation_rules(data, transformation_rules)
            executions.append(WorkExecution.objects.create(
                work=work,
                status="success",
                message="Transformaciones aplicadas correctamente",
                response=json.dumps(data)[:2000],
            ))

        # --- Guardado o envío ---
        if operation_type == "destiny":
            if origin_type in ["rest"]:
                method = conf.get("method", "get").lower()
                path = conf.get("path")
                payload = input_data[0].get("payload")
                if mapping:
                    payload_mapped = map_payload(mapping, payload)
                    work = Work.objects.get(id=1)
                    aja = ""
                #data = http_request_data(conn, conf, method=method, data=payload, path_override=path)

            elif origin_type in ["sftp", "ftp"]:
                content = json.dumps(data, indent=2)
                out_filename = conf.get("filename", f"{work.name}.json")
                write_to_ftp_or_sftp(conn, content=content, filename=out_filename)

            elif origin_type == "postgresql":
                table = conf.get("table")
                now = datetime.now().isoformat()
                if table:
                    for row in data:
                        row["ingested_at"] = now
                        insert_into_postgres(conn, table, row)
                else:
                    payload = data[0] if len(data) == 1 else data
                    insert_into_fallback_table(conn,conf, work.id, payload, now)

            elif origin_type == "restlet":
                had_errors = False
                important_keys = ["action", "recordType", "customform"]

                for row in data[:100]:
                    try:
                        # Reordenar claves importantes
                        ordered_row = OrderedDict()
                        for key in important_keys:
                            if key in row:
                                ordered_row[key] = row[key]
                        for key, value in row.items():
                            if key not in important_keys:
                                ordered_row[key] = value

                        result = send_to_netsuite(conf, conn, ordered_row)
                        status = "success" if result.get("ok") else "error"
                        message = result.get("message", "")
                        status_code = result.get("status_code", 200)

                    except Exception as e:
                        status = "error"
                        message = f"Exception sending to NetSuite: {str(e)}"
                        result = {"error": message}
                        status_code = getattr(e.response, "status_code", 500) if hasattr(e, "response") else 500
                        had_errors = True

                    executions.append(WorkExecution.objects.create(
                        work=work,
                        status=status,
                        message=message,
                        request=json.dumps(ordered_row),
                        response=json.dumps({"result": result, "status_code": status_code}),
                    ))

                if had_errors:
                    logger.warning(f"Some rows failed in NetSuite restlet call for work {work.id}")

            elif origin_type == "shopify":
                pass
            elif origin_type is None:
                pass
            else:
                raise ValueError(f"Unsupported connection type: {origin_type}")

            executions.append(WorkExecution.objects.create(
                work=work,
                status="success",
                message="Work completado exitosamente",
            ))

    except Exception as e:
        executions.append(WorkExecution.objects.create(
            work=work,
            status="error",
            message=f"Error en ejecución del Work: {str(e)}",
        ))
        logger.exception(f"❌ Error al ejecutar Work {work.id}: {str(e)}")
        raise

    return data, executions