from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.deps import get_db
from backend.model.chat import ChatSession, ChatMessage
from backend.schemas.chat import ChatSessionCreate, ChatSessionResponse, ChatMessageResponse, ChatMessageCreate
from backend.api.v1.auth import verify_token

router = APIRouter(tags=["Chats"])

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    payload: ChatSessionCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    session = ChatSession(
        user_id=user["uid"],
        title=payload.title
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user["uid"]).order_by(ChatSession.created_at.desc()).all()
    return sessions

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user["uid"]).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return messages
