import httpx
from typing import Dict, List, Any
from config.settings import settings
import structlog

logger = structlog.get_logger()


def inspect_database_schema(
    host: str = settings.DB_HOST,
    port: int = settings.DB_PORT,
    user: str = settings.DB_USER,
    password: str = settings.DB_PASSWORD,
    database: str = settings.DB_NAME
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Introspects ClickHouse database to retrieve tables, columns, data types, and nullability.
    """
    schema_info: Dict[str, List[Dict[str, Any]]] = {}
    endpoint_url = f"http://{host}:{port}/"
    sql = f"""
        SELECT 
            table, 
            name AS column_name, 
            type AS data_type,
            type LIKE '%Nullable%' AS is_nullable
        FROM system.columns
        WHERE database IN ('{database}', 'default')
        ORDER BY table, position FORMAT JSON;
    """
    try:
        auth = (user, password)
        params = {"database": database, "readonly": 1}
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(endpoint_url, params=params, auth=auth, content=sql)
            if resp.status_code == 200:
                rows = resp.json().get("data", [])
                for row in rows:
                    table_name = row.get("table", "")
                    column_name = row.get("column_name", "")
                    data_type = row.get("data_type", "")
                    is_nullable = bool(row.get("is_nullable", False))
                    if table_name not in schema_info:
                        schema_info[table_name] = []
                    schema_info[table_name].append({
                        "column_name": column_name,
                        "data_type": data_type,
                        "is_nullable": is_nullable
                    })
            else:
                logger.error("ClickHouse schema introspection HTTP error", status_code=resp.status_code, response=resp.text)
    except Exception as e:
        logger.error("Database schema introspection failed", error=str(e))

    return schema_info
