from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import json

from core.database import get_db, ChatSession, ChatMessage, SessionLocal
from services.ai_service import generate_chat_response
from core.config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with AI assistant"""
    
    # Create or get session
    if not chat_request.session_id:
        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            user_email=chat_request.user_email,
            user_name=chat_request.user_name
        )
        db.add(session)
        db.commit()
    else:
        session_id = chat_request.session_id
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Generate AI response
    ai_response = await generate_chat_response(chat_request.message, session_id)
    
    # Save messages to database
    user_message = ChatMessage(
        session_id=session_id,
        message=chat_request.message,
        response=ai_response,
        is_user_message=True
    )
    
    ai_message = ChatMessage(
        session_id=session_id,
        message=chat_request.message,
        response=ai_response,
        is_user_message=False
    )
    
    db.add(user_message)
    db.add(ai_message)
    db.commit()
    
    # Update session activity
    session.last_activity = datetime.utcnow()
    db.commit()
    
    return ChatResponse(
        response=ai_response,
        session_id=session_id,
        timestamp=datetime.utcnow().isoformat()
    )

@router.get("/chat/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a session"""
    
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    return ChatHistoryResponse(
        session_id=session_id,
        messages=[
            {
                "message": msg.message,
                "response": msg.response,
                "is_user_message": msg.is_user_message,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    )

@router.get("/chat/sessions")
async def get_chat_sessions(
    user_email: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get chat sessions for a user"""
    
    query = db.query(ChatSession)
    if user_email:
        query = query.filter(ChatSession.user_email == user_email)
    
    sessions = query.order_by(ChatSession.last_activity.desc()).limit(limit).all()
    
    return [
        {
            "session_id": session.session_id,
            "user_name": session.user_name,
            "user_email": session.user_email,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }
        for session in sessions
    ]

@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session and all its messages"""
    
    # Delete messages first
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    
    # Delete session
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if session:
        db.delete(session)
    
    db.commit()
    
    return {"message": "Chat session deleted successfully"}

@router.websocket("/chat/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    
    await manager.connect(websocket, session_id)
    
    # Create or get session
    db = SessionLocal()
    try:
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            session = ChatSession(session_id=session_id)
            db.add(session)
            db.commit()
        
        # Send welcome message
        welcome_message = {
            "type": "system",
            "message": "Welcome to Spa AI Assistant! How can I help you today?",
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_message))
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Generate AI response
                ai_response = await generate_chat_response(message_data["message"], session_id)
                
                # Save to database
                user_message = ChatMessage(
                    session_id=session_id,
                    message=message_data["message"],
                    response=ai_response,
                    is_user_message=True
                )
                
                ai_message = ChatMessage(
                    session_id=session_id,
                    message=message_data["message"],
                    response=ai_response,
                    is_user_message=False
                )
                
                db.add(user_message)
                db.add(ai_message)
                db.commit()
                
                # Update session activity
                session.last_activity = datetime.utcnow()
                db.commit()
                
                # Send response back to client
                response_data = {
                    "type": "ai_response",
                    "message": ai_response,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send_text(json.dumps(response_data))
                
        except WebSocketDisconnect:
            manager.disconnect(session_id)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        db.close()

@router.post("/chat/quick-response")
async def get_quick_response(
    message: str,
    db: Session = Depends(get_db)
):
    """Get a quick AI response without creating a session"""
    
    ai_response = await generate_chat_response(message, "quick")
    
    return {
        "response": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    }
