from agent.state import SQLAgentState
from database.connection import db_service
import structlog

logger = structlog.get_logger()


async def execute_sql_node(state: SQLAgentState) -> SQLAgentState:
    if not state.validated_sql:
        state.execution_error = "Cannot execute null or unvalidated SQL."
        state.status = "error"
        return state

    results, errors = db_service.execute_query(state.validated_sql)

    if errors:
        state.execution_error = "; ".join(errors)
        state.execution_result = None
        logger.error("SQL execution failed", error=state.execution_error)
    else:
        state.execution_result = results
        state.execution_error = None
        logger.info("SQL execution succeeded", row_count=len(results))

    return state
