from typing import Tuple, List
from security.sql_parser import parse_sql, SQLParsedInfo
from security.allowlist import ALLOWED_TABLES, ALLOWED_COLUMNS
from security.sensitive_columns import SENSITIVE_COLUMNS
from security.query_limits import MAX_SQL_LENGTH, MAX_JOINS
from database.connection import db_service
from config.settings import settings
import structlog

logger = structlog.get_logger()

FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE",
    "GRANT", "REVOKE", "MERGE", "CALL", "DO", "COPY", "VACUUM", "REINDEX",
    "LOCK", "EXPLAIN ANALYZE", "PG_READ_FILE", "PG_LS_DIR", "PG_EXEC",
    "PG_SLEEP", "SYSTEM", "EXEC", "EXECUTE"
}


class SQLValidator:
    def __init__(
        self,
        allowed_tables: set = ALLOWED_TABLES,
        allowed_columns: dict = ALLOWED_COLUMNS,
        sensitive_columns: set = SENSITIVE_COLUMNS,
        max_length: int = MAX_SQL_LENGTH,
        max_joins: int = MAX_JOINS,
        max_cost: float = settings.MAX_QUERY_COST
    ):
        self.allowed_tables = allowed_tables
        self.allowed_columns = allowed_columns
        self.sensitive_columns = sensitive_columns
        self.max_length = max_length
        self.max_joins = max_joins
        self.max_cost = max_cost

    def validate(self, sql: str) -> Tuple[bool, List[str], str]:
        """
        Validates SQL against security policy.
        Returns tuple: (is_valid: bool, errors: List[str], sanitized_sql: str)
        """
        errors: List[str] = []

        if not sql or not sql.strip():
            return False, ["SQL string is empty."], ""

        clean_sql = sql.strip().rstrip(";")

        # 1. Length Check
        if len(clean_sql) > self.max_length:
            errors.append(f"SQL query exceeds maximum allowed length of {self.max_length} characters.")

        # 2. Forbidden Keyword Check
        sql_upper = clean_sql.upper()
        for forbidden in FORBIDDEN_KEYWORDS:
            # Check standalone keyword occurrences
            if f" {forbidden} " in f" {sql_upper} " or sql_upper.startswith(f"{forbidden} ") or f"\n{forbidden}" in sql_upper:
                errors.append(f"Forbidden keyword detected in query: '{forbidden}'.")

        # 3. AST Parsing
        parsed: SQLParsedInfo = parse_sql(clean_sql)
        if not parsed.is_valid_syntax:
            errors.append(f"Syntax error: {parsed.parse_error}")
            return False, errors, clean_sql

        # 4. Single Statement Check
        if parsed.statements_count != 1:
            errors.append(f"Multiple statements are strictly forbidden. Found {parsed.statements_count} statements.")

        # 5. Statement Type Check (SELECT or WITH SELECT)
        if parsed.statement_type not in ("SELECT", "WITH"):
            errors.append(f"Only SELECT queries are permitted. Got '{parsed.statement_type}'.")

        # 6. Table Allowlist Check
        if not parsed.tables:
            errors.append("No valid target tables found in query.")
        for table in parsed.tables:
            if table not in self.allowed_tables:
                errors.append(f"Table '{table}' is not in the allowlist.")

        # 7. Sensitive Column & Column Allowlist Check
        for col_name in parsed.raw_column_names:
            if col_name in self.sensitive_columns:
                errors.append(f"Access to sensitive column '{col_name}' is strictly forbidden.")

        # 8. SELECT * Restriction
        if parsed.has_select_star:
            errors.append("SELECT * is forbidden. Specify explicit column names.")

        # 9. Join Limit Check
        if parsed.join_count > self.max_joins:
            errors.append(f"Query exceeds maximum allowed JOINs ({parsed.join_count} > {self.max_joins}).")

        if errors:
            logger.warning("SQL validation failed", errors=errors, sql=clean_sql)
            return False, errors, clean_sql

        # 10. EXPLAIN Cost Guardrail Check
        cost, explain_err = db_service.explain_query_cost(clean_sql)
        if explain_err:
            logger.warning("Cost evaluation error", error=explain_err)
        elif cost > self.max_cost:
            errors.append(f"Estimated query cost ({cost:.2f}) exceeds maximum threshold ({self.max_cost:.2f}).")
            return False, errors, clean_sql

        return True, [], clean_sql


sql_validator = SQLValidator()
