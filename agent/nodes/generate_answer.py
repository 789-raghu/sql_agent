from agent.state import SQLAgentState
from llm.client import local_llm_client
from agent.prompts.answer_generation import SYSTEM_ANSWER_GENERATION_PROMPT, USER_ANSWER_GENERATION_PROMPT
import json
import structlog

logger = structlog.get_logger()


async def generate_answer_node(state: SQLAgentState) -> SQLAgentState:
    if state.execution_result is None:
        if state.execution_error:
            if "timed out" in state.execution_error.lower():
                state.final_answer = "The ClickHouse database query timed out. The table may be large or the network is slow. Try a more specific query with filters."
            else:
                state.final_answer = f"Query execution failed: {state.execution_error}"
        elif state.validation_errors:
            state.final_answer = f"I could not execute a safe query due to security policy violations: {'; '.join(state.validation_errors)}"
        else:
            state.final_answer = "Unable to complete query execution."
        state.status = "error"
        return state

    if len(state.execution_result) == 0:
        state.final_answer = "The query ran successfully but returned no matching rows. Try adjusting your filters or question."
        state.status = "success"
        return state

    messages = [
        {"role": "system", "content": SYSTEM_ANSWER_GENERATION_PROMPT},
        {
            "role": "user",
            "content": USER_ANSWER_GENERATION_PROMPT.format(
                question=state.user_question,
                results=json.dumps(state.execution_result[:20], default=str, indent=2)
            )
        }
    ]

    answer = await local_llm_client.chat_completion(messages=messages, max_tokens=256, temperature=0.0)

    # Fallback response formatting if LLM response is simple/unreachable
    if not answer or "error" in answer.lower() or answer.startswith("{"):
        # Format clean summary from first result row
        first_row = state.execution_result[0]
        if "avg_consumption" in first_row:
            raw_val = first_row["avg_consumption"]
            if raw_val is not None:
                val = round(float(raw_val), 2)
                answer = f"The average consumption was {val} kWh."
            else:
                answer = "No consumption records were found for that period."
        elif "total_consumption" in first_row and "consumer_id" in first_row:
            answer = f"Found {len(state.execution_result)} consumers. Top consumer: {first_row.get('consumer_name', first_row['consumer_id'])} with {round(float(first_row['total_consumption']), 2)} kWh."
        elif "cluster_name" in first_row:
            answer = f"Cluster consumption summary: Top cluster is {first_row['cluster_name']} with average consumption of {round(float(first_row.get('cluster_avg_consumption', 0)), 2)} kWh."
        elif "total_consumers" in first_row:
            answer = f"Total consumers count: {first_row['total_consumers']}."
        else:
            formatted_rows = [", ".join(f"{k}: {v}" for k, v in row.items()) for row in state.execution_result[:5]]
            answer = f"Found {len(state.execution_result)} record(s):\n" + "\n".join(formatted_rows)

    state.final_answer = answer
    state.status = "success"
    logger.info("Generated final answer", answer=answer)
    return state
