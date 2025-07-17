import psycopg2
import json
from psycopg2.extras import RealDictCursor, Json
from contextlib import contextmanager
from psycopg2 import sql
from datetime import datetime, date

@contextmanager
def get_postgres_connection(config):
    conn = psycopg2.connect(
        dbname=config["dbname"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config.get("port", 5432)
    )
    try:
        yield conn
    finally:
        conn.close()

def select_from_postgres(connection, table, where_clause=None, params=None, queryParams=None):
    cfg = connection.config
    with get_postgres_connection(cfg) as conn:
        query = ""
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if query:
            query=queryParams
        else:
            query = f"SELECT * FROM {table}"
            if where_clause:
                query += f" WHERE {where_clause}"
        cur.execute(query, params or ())
        result = cur.fetchall()
        cur.close()
        return json.dumps([dict(r) for r in result], default=str)

def infer_pg_type(value):
    if value is None:
        return "TEXT"  # Default for nulls

    elif isinstance(value, bool):
        return "BOOLEAN"
    
    elif isinstance(value, int):
        return "INTEGER"
    
    elif isinstance(value, float):
        return "NUMERIC"

    elif isinstance(value, (datetime, date)):
        return "TIMESTAMP"

    elif isinstance(value, (dict, list)):
        return "JSONB"

    elif isinstance(value, str):
        return "TEXT"

    else:
        # Fallback for unknown Python types
        return "TEXT"
    
def insert_into_postgres(connection, table, data: dict):
    cfg = connection.config
    with get_postgres_connection(cfg) as conn:
        cur = conn.cursor()

        data = dict(data)
        data.setdefault("ingested_at", datetime.now())

        columns = list(data.keys())
        values = [Json(v) if isinstance(v, (dict, list)) else v for v in data.values()]

        insert_query = sql.SQL("""
            INSERT INTO {table} ({fields}) 
            VALUES ({placeholders}) 
            RETURNING *;
        """).format(
            table=sql.Identifier(table),
            fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
            placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
        )

        try:
            cur.execute(insert_query, values)

        except psycopg2.errors.UndefinedTable:
            conn.rollback()

            # Detectar si el payload ya trae 'id'
            has_id = "id" in data

            # Crear definición de columnas dinámicamente
            create_cols = [
                f"{key} {infer_pg_type(val)}"
                for key, val in data.items()
                if key != "ingested_at"
            ]

            # Insertar id SERIAL si no viene en los datos
            if not has_id:
                create_cols.insert(0, "id SERIAL PRIMARY KEY")

            # Asegurar columna de timestamp
            create_cols.append("ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

            create_stmt = sql.SQL("""
                CREATE TABLE {table} (
                    {cols}
                )
            """).format(
                table=sql.Identifier(table),
                cols=sql.SQL(', ').join(sql.SQL(c) for c in create_cols)
            )

            cur.execute(create_stmt)
            conn.commit()

            # Reintenta la inserción
            cur.execute(insert_query, values)

        inserted = cur.fetchone()
        conn.commit()
        cur.close()
        return inserted

def insert_into_fallback_table(conn_cfg, conf,operation_id, data, now):
    conn_cfg = conn_cfg.config
    with psycopg2.connect(
        dbname=conn_cfg["dbname"],
        user=conn_cfg["user"],
        password=conn_cfg["password"],
        host=conn_cfg["host"],
        port=conn_cfg.get("port", 5432)
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orchestrator_data (
                    id SERIAL PRIMARY KEY,
                    operation_id INTEGER,
                    payload JSONB,
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            payload = data if isinstance(data, (dict, list)) else {"raw": str(data)}
            cur.execute(
                "INSERT INTO orchestrator_data (operation_id, payload, ingested_at) VALUES (%s, %s, %s)",
                (operation_id, Json(payload), now)
            )

def update_postgres(connection, table, data: dict, where_clause, params):
    cfg = connection.config
    with get_postgres_connection(cfg) as conn:
        cur = conn.cursor()
        set_clause = ', '.join([f"{k} = %s" for k in data])
        values = list(data.values()) + list(params)
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause} RETURNING *"
        cur.execute(query, values)
        updated = cur.fetchone()
        conn.commit()
        cur.close()
        return updated
