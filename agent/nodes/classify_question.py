from agent.state import SQLAgentState
import structlog

logger = structlog.get_logger()

UNSUPPORTED_KEYWORDS = [
    "weather tomorrow", "stock price", "football score", "tell me a joke", "recipe for"
]


async def classify_question_node(state: SQLAgentState) -> SQLAgentState:
    q = state.user_question.lower()

    for kw in UNSUPPORTED_KEYWORDS:
        if kw in q:
            state.question_category = "unsupported"
            state.final_answer = "I don't have enough database information to answer that question."
            state.status = "invalid_question"
            return state

    state.question_category = "database_query"
    return state
