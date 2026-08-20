from agent.state import SQLAgentState
from security.sql_validator import sql_validator
import structlog

logger = structlog.get_logger()


async def validate_sql_node(state: SQLAgentState) -> SQLAgentState:
    is_valid, errors, sanitized_sql = sql_validator.validate(state.generated_sql)

    if is_valid:
        state.validated_sql = sanitized_sql
        state.validation_errors = []
        logger.info("SQL validation passed", sql=sanitized_sql)
    else:
        state.validated_sql = None
        state.validation_errors = errors
        logger.warning("SQL validation failed", errors=errors, sql=state.generated_sql)

    return state
