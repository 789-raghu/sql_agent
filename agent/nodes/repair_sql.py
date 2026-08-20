import json
from agent.state import SQLAgentState
from llm.client import local_llm_client
from agent.prompts.sql_generation import SYSTEM_SQL_GENERATION_PROMPT
import structlog

logger = structlog.get_logger()


async def repair_sql_node(state: SQLAgentState) -> SQLAgentState:
    state.retry_count += 1
    error_details = state.execution_error or "; ".join(state.validation_errors)

    logger.info("Repairing SQL query", retry_count=state.retry_count, error=error_details)

    repair_prompt = f"""User Question: {state.user_question}

Previously Generated SQL:
{state.generated_sql}

Error Encountered:
{error_details}

Relevant Schema:
{state.relevant_schema}

Fix the SQL query to resolve the error. ONLY return a JSON object with keys "sql" and "tables_used".
"""

    messages = [
        {"role": "system", "content": SYSTEM_SQL_GENERATION_PROMPT},
        {"role": "user", "content": repair_prompt}
    ]

    llm_output = await local_llm_client.chat_completion(messages=messages, max_tokens=512, temperature=0.0)

    sql_candidate = ""
    try:
        if "```json" in llm_output:
            json_str = llm_output.split("```json")[1].split("```")[0].strip()
            data = json.loads(json_str)
            sql_candidate = data.get("sql", "")
        elif "```sql" in llm_output:
            sql_candidate = llm_output.split("```sql")[1].split("```")[0].strip()
        elif llm_output.startswith("{"):
            data = json.loads(llm_output)
            sql_candidate = data.get("sql", "")
        else:
            sql_candidate = llm_output.strip()
    except Exception:
        sql_candidate = llm_output.strip()

    state.generated_sql = sql_candidate
    return state
