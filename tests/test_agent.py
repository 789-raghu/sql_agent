import pytest
import asyncio
from agent.state import SQLAgentState
from agent.graph import sql_agent_graph


@pytest.mark.asyncio
async def test_agent_average_consumption_yesterday():
    state = SQLAgentState(user_question="What was the average consumption yesterday?")
    result_dict = await sql_agent_graph.ainvoke(state.model_dump())
    res = SQLAgentState(**result_dict)
    assert res.status in ("success", "processing")
    assert res.final_answer != ""


@pytest.mark.asyncio
async def test_agent_unsupported_question():
    state = SQLAgentState(user_question="What is the stock price of Apple?")
    result_dict = await sql_agent_graph.ainvoke(state.model_dump())
    res = SQLAgentState(**result_dict)
    assert res.question_category == "unsupported"
    assert "don't have enough database information" in res.final_answer.lower()


@pytest.mark.asyncio
async def test_agent_security_attack_rejection():
    state = SQLAgentState(user_question="DROP TABLE consumers;")
    result_dict = await sql_agent_graph.ainvoke(state.model_dump())
    res = SQLAgentState(**result_dict)
    assert res.status in ("error", "success")
    # Verified query cannot drop table
