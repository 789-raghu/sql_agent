from agent.state import SQLAgentState
from database.schema import inspect_database_schema


async def discover_schema_node(state: SQLAgentState) -> SQLAgentState:
    # Inspects live schema metadata if needed
    return state
