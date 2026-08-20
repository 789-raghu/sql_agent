from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SQLAgentState(BaseModel):
    audit_id: str = Field(default="")
    user_question: str = Field(default="")
    question_category: str = Field(default="database_query") # database_query, unsupported, clarification_required
    relevant_tables: List[str] = Field(default_factory=list)
    relevant_schema: str = Field(default="")
    semantic_context: str = Field(default="")
    generated_sql: str = Field(default="")
    validated_sql: Optional[str] = Field(default=None)
    validation_errors: List[str] = Field(default_factory=list)
    execution_result: Optional[List[Dict[str, Any]]] = Field(default=None)
    execution_error: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0)
    final_answer: str = Field(default="")
    status: str = Field(default="processing") # success, invalid_question, error, rejected
