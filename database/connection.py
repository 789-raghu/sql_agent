import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from typing import List, Dict, Any, Tuple
from config.settings import settings
import structlog

logger = structlog.get_logger()


class DatabaseService:
    def __init__(self, db_url: str = settings.DATABASE_URL, timeout_ms: int = settings.SQL_STATEMENT_TIMEOUT_MS):
        self.db_url = db_url
        self.timeout_ms = timeout_ms

    def execute_query(self, sql: str, max_rows: int = settings.MAX_RESULT_ROWS) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Executes a validated SELECT query on PostgreSQL using a read-only user and transaction.
        Sets statement timeout and bounds result size.
        Returns tuple of (results list, list of warnings/errors).
        """
        results: List[Dict[str, Any]] = []
        errors: List[str] = []

        try:
            with psycopg.connect(self.db_url, row_factory=dict_row) as conn:
                # Enforce statement timeout and read-only transaction mode
                with conn.cursor() as cur:
                    cur.execute(f"SET statement_timeout = '{self.timeout_ms}ms';")
                    cur.execute("SET TRANSACTION READ ONLY;")

                    cur.execute(sql)
                    rows = cur.fetchmany(max_rows + 1)

                    if len(rows) > max_rows:
                        rows = rows[:max_rows]
                        logger.warning("Query result truncated", max_rows=max_rows)

                    results = [dict(row) for row in rows]
                    conn.commit()

        except psycopg.Error as e:
            error_msg = f"Database execution error: {str(e)}"
            logger.error("Database query execution failed", error=str(e), sql=sql)
            errors.append(error_msg)

        except Exception as e:
            error_msg = f"Unexpected database error: {str(e)}"
            logger.error("Unexpected database failure", error=str(e), sql=sql)
            errors.append(error_msg)

        return results, errors

    def explain_query_cost(self, sql: str) -> Tuple[float, str | None]:
        """
        Executes plain EXPLAIN (without ANALYZE) to estimate total query cost.
        Returns (estimated_cost, error_message).
        """
        try:
            with psycopg.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SET statement_timeout = '{self.timeout_ms}ms';")
                    cur.execute(f"EXPLAIN {sql}")
                    explain_lines = cur.fetchall()

                    if explain_lines and len(explain_lines[0]) > 0:
                        first_line = explain_lines[0][0]
                        # First line usually looks like: 'Seq Scan on consumers  (cost=0.00..18.80 rows=880 width=218)'
                        if "cost=" in first_line:
                            cost_part = first_line.split("cost=")[1].split(" ")[0]
                            max_cost = float(cost_part.split("..")[1])
                            return max_cost, None

            return 0.0, None

        except Exception as e:
            return 999999.0, f"EXPLAIN cost check failed: {str(e)}"


db_service = DatabaseService()
