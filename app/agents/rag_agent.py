
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.rag.retriever import retrieve
from app.config import get_settings
import json

settings = get_settings()

RAG_SYSTEM_PROMPT = """You are a strict FAQ assistant. Answer the user's question using ONLY the context below.

The context contains FAQ entries numbered [1], [2], etc., ordered by relevance (most relevant first).

STRICT RULES:
1. Find the FAQ entry whose QUESTION is the closest or exact match to the user's question.
2. Return ONLY that entry's ANSWER — word for word if possible. Do not blend or combine answers from multiple entries.
3. If no entry closely matches the user's question, say: "I'm sorry, I couldn't find an answer to your question in the available FAQ data."
4. Never add information not present in the matching FAQ entry.

Context:
{context}"""

DECOMPOSE_PROMPT = """You are a query analyzer. The user may have asked multiple questions in one message.
Split the input into individual distinct questions. Return a JSON array of strings.
If it is already a single question, return a array with just that one question.

Examples:
Input: "What is the price and how long does shipping take?"
Output: ["What is the price?", "How long does shipping take?"]

Input: "What is the refund policy?"
Output: ["What is the refund policy?"]

Return ONLY the JSON array, no explanation."""

MERGE_PROMPT = """You are a helpful FAQ assistant. The user asked a multi-part question.
Below are the answers retrieved for each sub-question from the FAQ database.
Combine them into one clear, concise response. Only use the information provided — do not add anything extra.

{qa_pairs}"""

SIMILARITY_THRESHOLD = 0.6


def _get_llm():
    return ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )


def _retrieve_answer(query: str, llm: ChatOpenAI) -> str:
    hits = retrieve(query, top_k=4)
    relevant = [h for h in hits if h["distance"] <= SIMILARITY_THRESHOLD]

    if not relevant:
        return None

    context = "\n\n---\n\n".join(
        f"[{i+1}] {h['document']}" for i, h in enumerate(relevant)
    )
    messages = [
        SystemMessage(content=RAG_SYSTEM_PROMPT.format(context=context)),
        HumanMessage(content=query),
    ]
    return llm.invoke(messages).content.strip()


def run_rag_agent(query: str) -> str:
    llm = _get_llm()

    # Step 1 — detect and decompose multi-part questions
    decomp = llm.invoke([
        SystemMessage(content=DECOMPOSE_PROMPT),
        HumanMessage(content=query),
    ])
    try:
        sub_questions = json.loads(decomp.content.strip())
        if not isinstance(sub_questions, list) or len(sub_questions) == 0:
            sub_questions = [query]
    except Exception:
        sub_questions = [query]

    # Step 2 — single question: direct retrieval
    if len(sub_questions) == 1:
        answer = _retrieve_answer(sub_questions[0], llm)
        return answer or "I'm sorry, I couldn't find an answer to your question in the available FAQ data."

    # Step 3 — multiple questions: retrieve each independently then merge
    qa_pairs = []
    for sq in sub_questions:
        ans = _retrieve_answer(sq, llm)
        if ans:
            qa_pairs.append(f"Q: {sq}\nA: {ans}")

    if not qa_pairs:
        return "I'm sorry, I couldn't find answers to your questions in the available FAQ data."

    if len(qa_pairs) == 1:
        return qa_pairs[0].split("\nA: ", 1)[1]

    merged = llm.invoke([
        HumanMessage(content=MERGE_PROMPT.format(qa_pairs="\n\n".join(qa_pairs))),
    ])
    return merged.content.strip()