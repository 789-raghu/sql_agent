import sqlglot
from sqlglot import exp, parse_one
from typing import Set, List, Dict, Any, Tuple
import structlog

logger = structlog.get_logger()


class SQLParsedInfo:
    def __init__(self, raw_sql: str):
        self.raw_sql = raw_sql
        self.statements_count = 0
        self.expression: exp.Expression | None = None
        self.statement_type: str = ""
        self.tables: Set[str] = set()
        self.columns: Set[Tuple[str, str]] = set()  # (table_or_alias, column_name)
        self.raw_column_names: Set[str] = set()
        self.join_count: int = 0
        self.has_select_star: bool = False
        self.has_comments: bool = False
        self.is_valid_syntax: bool = False
        self.parse_error: str | None = None

        self._parse()

    def _parse(self):
        try:
            # Check for multiple statements
            parsed_list = sqlglot.parse(self.raw_sql, read="clickhouse")
            self.statements_count = len(parsed_list)

            if self.statements_count != 1:
                self.parse_error = f"Expected exactly 1 SQL statement, got {self.statements_count}."
                return

            self.expression = parsed_list[0]
            if self.expression is None:
                self.parse_error = "Failed to parse SQL expression."
                return

            self.is_valid_syntax = True

            # Statement type
            if isinstance(self.expression, exp.Select):
                self.statement_type = "SELECT"
            elif isinstance(self.expression, exp.Expression):
                self.statement_type = self.expression.key.upper()

            # Tables
            for table in self.expression.find_all(exp.Table):
                if table.name:
                    table_name = table.name.lower()
                    db_name = table.db.lower() if table.db else ""
                    self.tables.add(table_name)
                    if db_name:
                        self.tables.add(f"{db_name}.{table_name}")

            # Joins
            joins = list(self.expression.find_all(exp.Join))
            self.join_count = len(joins)

            # SELECT * check
            for star in self.expression.find_all(exp.Star):
                self.has_select_star = True

            # Columns
            for column in self.expression.find_all(exp.Column):
                col_name = column.name.lower() if column.name else ""
                table_name = column.table.lower() if column.table else ""
                if col_name:
                    self.raw_column_names.add(col_name)
                    self.columns.add((table_name, col_name))

            # Comments check
            if "--" in self.raw_sql or "/*" in self.raw_sql:
                self.has_comments = True

        except Exception as e:
            self.is_valid_syntax = False
            self.parse_error = f"SQL syntax error: {str(e)}"
            logger.warning("SQL parsing error", error=str(e), sql=self.raw_sql)


def parse_sql(sql: str) -> SQLParsedInfo:
    return SQLParsedInfo(sql)
