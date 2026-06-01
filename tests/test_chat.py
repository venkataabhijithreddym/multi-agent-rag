
from unittest.mock import patch


def test_chat_rag_agent(client, auth_headers):
    mock_result = {"answer": "BigRock offers domain registration and hosting.", "agent_used": "rag_agent"}
    with patch("app.api.chat.run_orchestrator", return_value=mock_result):
        response = client.post("/chat", json={"query": "What services does BigRock offer?"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == mock_result["answer"]
    assert data["agent_used"] == "rag_agent"


def test_chat_tool_agent(client, auth_headers):
    mock_result = {"answer": "Weather in London: Sunny, 22°C.", "agent_used": "tool_agent"}
    with patch("app.api.chat.run_orchestrator", return_value=mock_result):
        response = client.post("/chat", json={"query": "What is the weather in London?"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_used"] == "tool_agent"


def test_chat_requires_auth(client):
    response = client.post("/chat", json={"query": "hello"})
    assert response.status_code == 401


def test_chat_empty_query(client, auth_headers):
    mock_result = {"answer": "I'm sorry, I couldn't find an answer.", "agent_used": "rag_agent"}
    with patch("app.api.chat.run_orchestrator", return_value=mock_result):
        response = client.post("/chat", json={"query": ""}, headers=auth_headers)
    assert response.status_code == 200