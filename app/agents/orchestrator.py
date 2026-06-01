

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from app.agents.intent_classifier import AgentState, classify_intent
from app.agents.rag_agent import run_rag_agent
from app.agents.tool_agent import run_tool_agent


# --- Graph nodes ---

def node_classify(state: AgentState) -> AgentState:
    intent = classify_intent(state["query"])
    return {**state, "intent": intent}


def node_rag(state: AgentState) -> AgentState:
    answer = run_rag_agent(state["query"])
    return {**state, "answer": answer, "agent_used": "rag_agent"}


def node_tool(state: AgentState) -> AgentState:
    answer = run_tool_agent(state["query"])
    return {**state, "answer": answer, "agent_used": "tool_agent"}


def route(state: AgentState) -> Literal["rag_agent", "tool_agent"]:
    return "tool_agent" if state["intent"] == "tool" else "rag_agent"


# --- Build the graph ---

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("classifier", node_classify)
    graph.add_node("rag_agent", node_rag)
    graph.add_node("tool_agent", node_tool)

    graph.set_entry_point("classifier")
    graph.add_conditional_edges("classifier", route, {"rag_agent": "rag_agent", "tool_agent": "tool_agent"})
    graph.add_edge("rag_agent", END)
    graph.add_edge("tool_agent", END)

    return graph.compile()


# Singleton compiled graph
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_orchestrator(query: str) -> dict:
    graph = get_graph()
    initial_state: AgentState = {
        "query": query,
        "intent": "unknown",
        "answer": "",
        "agent_used": "",
    }
    result = graph.invoke(initial_state)
    return {"answer": result["answer"], "agent_used": result["agent_used"]}