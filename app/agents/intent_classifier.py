
from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import get_settings

settings = get_settings()


class AgentState(TypedDict):
    query: str
    intent: Literal["rag", "tool", "unknown"]
    answer: str
    agent_used: str


INTENT_SYSTEM_PROMPT = """You are an intent classifier for a multi-agent system.
Given a user query, classify it into one of these categories:

- "tool": The user is asking about weather, forecasts, OR wants to manage tasks/todos (create, list, update, delete tasks).
- "rag": The user is asking a general FAQ question about BigRock services, domains, hosting, affiliate program, or any other general knowledge question.

Respond with ONLY one word: either "tool" or "rag". No explanation."""


def classify_intent(query: str) -> Literal["rag", "tool"]:
    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )
    messages = [
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=query),
    ]
    response = llm.invoke(messages)
    intent = response.content.strip().lower()
    return "tool" if intent == "tool" else "rag"