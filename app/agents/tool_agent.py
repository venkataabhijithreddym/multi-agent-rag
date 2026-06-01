
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from app.tools import get_weather, todo_create_task, todo_list_tasks, todo_update_task, todo_delete_task
from app.config import get_settings

settings = get_settings()

TOOL_SYSTEM_PROMPT = """You are a helpful assistant that can:
1. Get current weather information for any city.
2. Manage todo tasks: create, list, update, and delete tasks.

Use the appropriate tool to answer the user's request. Be concise and helpful."""


def run_tool_agent(query: str) -> str:
    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )
    tools = [get_weather, todo_create_task, todo_list_tasks, todo_update_task, todo_delete_task]
    agent = create_react_agent(llm, tools, prompt=TOOL_SYSTEM_PROMPT)

    result = agent.invoke({"messages": [("human", query)]})
    messages = result.get("messages", [])
    # Last message is the final AI response
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content and msg.__class__.__name__ == "AIMessage":
            return msg.content.strip()
    return "I was unable to process your request with the available tools."