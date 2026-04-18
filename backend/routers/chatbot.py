from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.core.dependencies import get_current_farmer
from backend.services.groq_service import ask_chatbot
from backend.models.user import User

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    conversation_history: list = []


class ChatResponse(BaseModel):
    answer: str
    model_used: str


@router.post("/ask", response_model=ChatResponse)
def chat(payload: ChatRequest, current_user: User = Depends(get_current_farmer)):
    answer = ask_chatbot(payload.question, payload.conversation_history)
    return ChatResponse(answer=answer, model_used="llama-3.1-8b-instant")
