from agent.state import SQLAgentState
from semantic.retriever import schema_retriever


async def retrieve_schema_node(state: SQLAgentState) -> SQLAgentState:
    retrieved = schema_retriever.retrieve(state.user_question)
    state.relevant_tables = retrieved["relevant_tables"]
    state.relevant_schema = retrieved["schema_prompt"]
    state.semantic_context = f"Relationships:\n{retrieved['relationships_prompt']}\n\nDefinitions:\n{retrieved['definitions_prompt']}"
    return state
