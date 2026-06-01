
from fastapi import APIRouter, Depends
from app.agents.orchestrator import run_orchestrator
from app.auth.dependencies import get_current_user
from app.database import User
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    result = run_orchestrator(payload.query)
    return ChatResponse(answer=result["answer"], agent_used=result["agent_used"])