from .operation_handlers import HANDLER_MAP

def run_operation(operation):
    conn = operation.connection
    op_type = operation.operation_type.lower()
    conn_type = conn.type.upper()

    handler = HANDLER_MAP.get(conn_type)
    if not handler:
        return {"status": "unsupported_connection_type", "type": conn_type}

    if op_type == "origin":
        return handler.run_origin(conn, operation)
    elif op_type == "destiny":
        return handler.run_destiny(conn, operation)

    return {"status": "invalid_operation_type"}