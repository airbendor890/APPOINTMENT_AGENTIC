from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from .. import models, schemas
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=schemas.ChatResponse)
def chat_with_llm(request: schemas.ChatRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Takes session_id and user input text,
    runs it through LangGraph AI pipeline, 
    returns generated output.
    """

     # Validate session_id
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    

    # Call your LangGraph pipeline
    llm_output = run_langgraph_pipeline(
        session_id=request.session_id,
        user_id=user.id,
        input_text=request.input_text
    )

    return schemas.ChatResponse(
        session_id=request.session_id,
        user_input=request.input_text,
        llm_output=llm_output
    )
    

# Dummy LangGraph runner (replace with real LangGraph integration)
def run_langgraph_pipeline(session_id: str, user_id: int, input_text: str) -> dict:
    # Here you’d invoke your LangGraph chat graph
    return {
        "output": "AI response goes here",
        "session_id": session_id,
    }