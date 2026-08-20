import asyncio
import time
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from agent.state import SQLAgentState
from agent.graph import sql_agent_graph
from audit_logging.audit import audit_logger
from config.settings import settings
import structlog

logger = structlog.get_logger()

router = APIRouter()

# Concurrency semaphore for CPU-bound LLM inference
concurrency_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_LLM_REQUESTS)


class QueryRequest(BaseModel):
    question: str = Field(..., example="What was the average consumption yesterday?")
    include_sql: Optional[bool] = Field(default=False, description="Whether to include generated SQL in response.")


class QueryResponse(BaseModel):
    answer: str
    sql: Optional[str] = None
    execution_time_ms: float
    status: str
    tables_used: List[str] = Field(default_factory=list)
    audit_id: str


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    start_time = time.time()
    audit_id = str(uuid.uuid4())

    state = SQLAgentState(
        audit_id=audit_id,
        user_question=request.question.strip()
    )

    async with concurrency_semaphore:
        try:
            final_state_dict = await sql_agent_graph.ainvoke(state.model_dump())
            final_state = SQLAgentState(**final_state_dict)
        except Exception as e:
            logger.error("Agent execution error", error=str(e), question=request.question)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            state.final_answer = f"Error processing request: {str(e)}"
            state.status = "error"
            audit_logger.log_agent_execution(state, duration_ms)
            return QueryResponse(
                answer=state.final_answer,
                sql=state.validated_sql if request.include_sql else None,
                execution_time_ms=duration_ms,
                status="error",
                audit_id=audit_id
            )

    duration_ms = round((time.time() - start_time) * 1000, 2)
    audit_logger.log_agent_execution(final_state, duration_ms)

    return QueryResponse(
        answer=final_state.final_answer,
        sql=final_state.validated_sql if request.include_sql else None,
        execution_time_ms=duration_ms,
        status=final_state.status,
        tables_used=final_state.relevant_tables,
        audit_id=audit_id
    )
