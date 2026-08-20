from langgraph.graph import StateGraph, END
from agent.state import SQLAgentState
from agent.nodes.classify_question import classify_question_node
from agent.nodes.discover_schema import discover_schema_node
from agent.nodes.retrieve_schema import retrieve_schema_node
from agent.nodes.generate_sql import generate_sql_node
from agent.nodes.validate_sql import validate_sql_node
from agent.nodes.execute_sql import execute_sql_node
from agent.nodes.repair_sql import repair_sql_node
from agent.nodes.generate_answer import generate_answer_node
from config.settings import settings
import structlog

logger = structlog.get_logger()


def route_classification(state: SQLAgentState) -> str:
    if state.question_category != "database_query":
        return "end"
    return "discover_schema"


def route_validation(state: SQLAgentState) -> str:
    if state.validated_sql is not None:
        return "execute_sql"

    if state.retry_count < settings.MAX_SQL_RETRIES:
        return "repair_sql"

    return "generate_answer"


def route_execution(state: SQLAgentState) -> str:
    if state.execution_error is not None and state.retry_count < settings.MAX_SQL_RETRIES:
        return "repair_sql"

    return "generate_answer"


def build_sql_agent_graph():
    builder = StateGraph(SQLAgentState)

    # Add Nodes
    builder.add_node("classify_question", classify_question_node)
    builder.add_node("discover_schema", discover_schema_node)
    builder.add_node("retrieve_schema", retrieve_schema_node)
    builder.add_node("generate_sql", generate_sql_node)
    builder.add_node("validate_sql", validate_sql_node)
    builder.add_node("execute_sql", execute_sql_node)
    builder.add_node("repair_sql", repair_sql_node)
    builder.add_node("generate_answer", generate_answer_node)

    # Set Entry Point
    builder.set_entry_point("classify_question")

    # Edges
    builder.add_conditional_edges(
        "classify_question",
        route_classification,
        {"discover_schema": "discover_schema", "end": END}
    )

    builder.add_edge("discover_schema", "retrieve_schema")
    builder.add_edge("retrieve_schema", "generate_sql")
    builder.add_edge("generate_sql", "validate_sql")

    builder.add_conditional_edges(
        "validate_sql",
        route_validation,
        {
            "execute_sql": "execute_sql",
            "repair_sql": "repair_sql",
            "generate_answer": "generate_answer"
        }
    )

    builder.add_conditional_edges(
        "execute_sql",
        route_execution,
        {
            "repair_sql": "repair_sql",
            "generate_answer": "generate_answer"
        }
    )

    builder.add_edge("repair_sql", "validate_sql")
    builder.add_edge("generate_answer", END)

    return builder.compile()


sql_agent_graph = build_sql_agent_graph()
