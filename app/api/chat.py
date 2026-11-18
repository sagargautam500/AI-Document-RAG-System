
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import ask_question


router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):

    session_id: str = Field(min_length=1)

    question: str = Field(min_length=1)

    limit: int = Field(default=5, ge=1, le=20)


@router.post("/ask")
def chat(request: ChatRequest):

    try:
        return ask_question(
            question=request.question,
            session_id=request.session_id,
            limit=request.limit
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(error)}"
        )
