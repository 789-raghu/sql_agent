import psycopg
from typing import Dict, List, Any
from config.settings import settings
import structlog

logger = structlog.get_logger()


def inspect_database_schema(db_url: str = settings.DATABASE_URL) -> Dict[str, List[Dict[str, Any]]]:
    """
    Introspects PostgreSQL database to retrieve public tables, columns, data types, and nullability.
    """
    schema_info: Dict[str, List[Dict[str, Any]]] = {}
    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        table_name, 
                        column_name, 
                        data_type,
                        is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position;
                """)
                rows = cur.fetchall()
                for table_name, column_name, data_type, is_nullable in rows:
                    if table_name not in schema_info:
                        schema_info[table_name] = []
                    schema_info[table_name].append({
                        "column_name": column_name,
                        "data_type": data_type,
                        "is_nullable": is_nullable == 'YES'
                    })
    except Exception as e:
        logger.error("Database schema introspection failed", error=str(e))

    return schema_info
