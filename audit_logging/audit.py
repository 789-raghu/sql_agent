import time
import uuid
from typing import Dict, Any, List, Optional
import structlog
from agent.state import SQLAgentState

logger = structlog.get_logger("audit")


class AuditLogger:
    def log_agent_execution(self, state: SQLAgentState, execution_duration_ms: float):
        audit_record = {
            "audit_id": state.audit_id or str(uuid.uuid4()),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "user_question": state.user_question,
            "question_category": state.question_category,
            "relevant_tables": state.relevant_tables,
            "generated_sql": state.generated_sql,
            "validated_sql": state.validated_sql,
            "validation_errors": state.validation_errors,
            "execution_error": state.execution_error,
            "execution_duration_ms": execution_duration_ms,
            "rows_returned": len(state.execution_result) if state.execution_result is not None else 0,
            "retry_count": state.retry_count,
            "status": state.status,
            "final_answer": state.final_answer[:200] if state.final_answer else ""
        }

        logger.info("AUDIT_LOG_ENTRY", **audit_record)
        return audit_record


audit_logger = AuditLogger()
