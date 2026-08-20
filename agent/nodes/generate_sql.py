import json
from agent.state import SQLAgentState
from llm.client import local_llm_client
from agent.prompts.sql_generation import SYSTEM_SQL_GENERATION_PROMPT, USER_SQL_GENERATION_PROMPT
import structlog

logger = structlog.get_logger()


async def generate_sql_node(state: SQLAgentState) -> SQLAgentState:
    messages = [
        {"role": "system", "content": SYSTEM_SQL_GENERATION_PROMPT},
        {
            "role": "user",
            "content": USER_SQL_GENERATION_PROMPT.format(
                question=state.user_question,
                schema=state.relevant_schema,
                relationships=state.semantic_context,
                definitions=""
            )
        }
    ]

    llm_output = await local_llm_client.chat_completion(messages=messages, max_tokens=512, temperature=0.0)

    # Extract JSON or raw SQL
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
    except Exception as e:
        logger.warning("Failed to parse JSON from LLM SQL generation", raw=llm_output, error=str(e))
        sql_candidate = llm_output.strip()

    state.generated_sql = sql_candidate
    logger.info("Generated SQL", sql=sql_candidate)
    return state
