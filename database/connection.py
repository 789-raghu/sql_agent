import json
import httpx
from typing import List, Dict, Any, Tuple
from config.settings import settings
import structlog

logger = structlog.get_logger()


class DatabaseService:
    def __init__(
        self,
        host: str = settings.DB_HOST,
        port: int = settings.DB_PORT,
        user: str = settings.DB_USER,
        password: str = settings.DB_PASSWORD,
        database: str = settings.DB_NAME,
        timeout_ms: int = settings.SQL_STATEMENT_TIMEOUT_MS
    ):
        self.endpoint_url = f"http://{host}:{port}/"
        self.user = user
        self.password = password
        self.database = database
        self.timeout_sec = max(1.0, timeout_ms / 1000.0)

    def execute_query(self, sql: str, max_rows: int = settings.MAX_RESULT_ROWS) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Executes a validated SELECT query on ClickHouse via the HTTP interface using read-only credentials.
        Returns tuple of (results list, list of warnings/errors).
        """
        results: List[Dict[str, Any]] = []
        errors: List[str] = []

        clean_sql = sql.strip().rstrip(";")
        if "FORMAT" not in clean_sql.upper():
            formatted_sql = f"{clean_sql} FORMAT JSON;"
        else:
            formatted_sql = f"{clean_sql};"

        try:
            params = {
                "database": self.database,
                "max_execution_time": int(self.timeout_sec),
                "readonly": 1
            }
            auth = (self.user, self.password)

            with httpx.Client(timeout=self.timeout_sec) as client:
                resp = client.post(
                    self.endpoint_url,
                    params=params,
                    auth=auth,
                    content=formatted_sql
                )

                if resp.status_code != 200:
                    error_msg = f"ClickHouse execution error (HTTP {resp.status_code}): {resp.text.strip()}"
                    logger.error("ClickHouse query failed", status_code=resp.status_code, response=resp.text, sql=clean_sql)
                    errors.append(error_msg)
                    return results, errors

                payload = resp.json()
                rows = payload.get("data", [])

                if len(rows) > max_rows:
                    rows = rows[:max_rows]
                    logger.warning("Query result truncated", max_rows=max_rows)

                results = rows

        except httpx.TimeoutException as e:
            error_msg = f"ClickHouse query execution timed out after {self.timeout_sec}s"
            logger.error("ClickHouse query timeout", error=str(e), sql=clean_sql)
            errors.append(error_msg)

        except Exception as e:
            error_msg = f"ClickHouse database error: {str(e)}"
            logger.error("ClickHouse database failure", error=str(e), sql=clean_sql)
            errors.append(error_msg)

        return results, errors

    def explain_query_cost(self, sql: str) -> Tuple[float, str | None]:
        """
        Executes EXPLAIN to validate query execution plan in ClickHouse.
        Returns (estimated_cost, error_message).
        """
        clean_sql = sql.strip().rstrip(";")
        if clean_sql.upper().startswith("EXPLAIN"):
            explain_sql = clean_sql
        else:
            explain_sql = f"EXPLAIN {clean_sql}"

        try:
            params = {
                "database": self.database,
                "max_execution_time": int(self.timeout_sec),
                "readonly": 1
            }
            auth = (self.user, self.password)

            with httpx.Client(timeout=self.timeout_sec) as client:
                resp = client.post(
                    self.endpoint_url,
                    params=params,
                    auth=auth,
                    content=explain_sql
                )

                if resp.status_code != 200:
                    return 999999.0, f"EXPLAIN failed (HTTP {resp.status_code}): {resp.text.strip()}"

                return 0.0, None

        except Exception as e:
            return 999999.0, f"EXPLAIN cost check failed: {str(e)}"


db_service = DatabaseService()
