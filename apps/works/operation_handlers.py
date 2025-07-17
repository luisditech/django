import json
import csv
import io
from datetime import datetime
import jmespath

from apps.connections.services import (
    http_request_data,
    read_from_ftp_or_sftp,
    write_to_ftp_or_sftp,
    select_from_postgres,
    insert_into_postgres,
)


class BaseHandler:
    def run_origin(self, connection, operation):
        raise NotImplementedError

    def run_destiny(self, connection, operation):
        raise NotImplementedError


def apply_operation_config(data, config, is_csv=False):
    if not config:
        return data

    # Parse CSV to JSON
    if is_csv and isinstance(data, str):
        reader = csv.DictReader(io.StringIO(data))
        data = list(reader)

    # Apply path extraction
    path = config.get("path")
    if path:
        data = jmespath.search(path, data)

    # Apply field mapping
    mapping = config.get("map")
    if mapping:
        if isinstance(data, list):
            data = [{new: item.get(old) for new, old in mapping.items()} for item in data]
        elif isinstance(data, dict):
            data = {new: data.get(old) for new, old in mapping.items()}

    return data


class HTTPHandler(BaseHandler):
    def run_origin(self, connection, operation):
        method = connection.config.get("method", "get").lower()
        payload = connection.config.get("payload")
        base_url = connection.config.get("base_url", "").rstrip("/")
        endpoint_path = connection.config.get("params", "").lstrip("/")
        full_url = f"{base_url}/{endpoint_path}"
        path_expr = connection.config.get("path")  # e.g., "data.results[0]"

        raw_data = http_request_data(
            connection,
            url=full_url,
            method=method,
            data=payload
        )

        if path_expr:
            try:
                raw_data = jmespath.search(path_expr, raw_data)
            except Exception as e:
                return {"status": "error", "message": f"Path resolution failed: {str(e)}"}

        data = apply_operation_config(raw_data, operation.origin_config)
        print(data)
        return {"status": "success", "source": "http", "data": data}

    def run_destiny(self, connection, operation):
        return {"status": "unsupported_destination", "type": "HTTP"}

class PostgresHandler(BaseHandler):
    def run_origin(self, connection, operation):
        table = connection.config.get("table")
        if not table:
            return {"status": "error", "message": "Missing 'table' in origin config"}

        where = connection.config.get("where_clause")
        params = connection.config.get("params")

        try:
            raw_data = select_from_postgres(connection, table, where_clause=where, params=params)
            data = apply_operation_config(raw_data, operation.origin_config)
            return {"status": "success", "source": "postgres", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_destiny(self, connection, operation):
        table = connection.config.get("table")
        if not table:
            return {"status": "error", "message": "Missing 'table' in destination config"}

        payload = connection.config.get("payload") or operation.destiny_config or {}
        if not payload:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "note": f"Work '{operation.name}' ran with no payload"
            }

        try:
            transformed = apply_operation_config(payload, operation.destiny_config or {})

            inserted = []
            now = datetime.now().isoformat()

            if isinstance(transformed, list):
                for row in transformed:
                    row["ingested_at"] = now
                    inserted.append(insert_into_postgres(connection, table, row))
            elif isinstance(transformed, dict):
                transformed["ingested_at"] = now
                inserted_row = insert_into_postgres(connection, table, transformed)
                inserted.append(inserted_row)
            else:
                return {"status": "error", "message": "Unsupported data format for insert"}

            return {
                "status": "success",
                "destination": "postgres",
                "rows_inserted": len(inserted)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

class SFTPHandler(BaseHandler):
    def run_origin(self, connection, operation):
        filename = connection.config.get("filename")
        if not filename:
            return {"status": "error", "message": "Missing filename in config"}

        raw_data = read_from_ftp_or_sftp(connection, filename)
        is_csv = connection.config.get("format") == "csv"
        data = apply_operation_config(raw_data, operation.origin_config, is_csv=is_csv)
        return {"status": "success", "source": "sftp", "data": data}

    def run_destiny(self, connection, operation):
        filename = connection.config.get("filename") or f"{operation.name}.json"
        payload = connection.config.get("payload", {"example": "output data"})
        transformed = apply_operation_config(payload, operation.destiny_config)
        content = (
            json.dumps(transformed, indent=2)
            if isinstance(transformed, (dict, list))
            else str(transformed)
        )
        write_to_ftp_or_sftp(connection, content=content, filename=filename)
        return {"status": "success", "destination": "sftp", "filename": filename}


class FTPHandler(SFTPHandler):
    pass


HANDLER_MAP = {
    "HTTP": HTTPHandler(),
    "POSTGRES": PostgresHandler(),
    "SFTP": SFTPHandler(),
    "FTP": FTPHandler(),
}