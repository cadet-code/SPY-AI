from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from core.database import get_db, CustomerInquiry, SessionLocal
from services.ai_service import generate_inquiry_response
from services.email_service import send_inquiry_response
from core.config import settings

router = APIRouter()

class InquiryRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str

class InquiryResponse(BaseModel):
    inquiry_id: int
    status: str
    ai_response: Optional[str] = None
    response_sent: bool = False

@router.post("/inquiry", response_model=InquiryResponse)
async def create_inquiry(
    inquiry_request: InquiryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new customer inquiry with AI-powered response"""
    
    # Create inquiry record
    inquiry = CustomerInquiry(
        name=inquiry_request.name,
        email=inquiry_request.email,
        phone=inquiry_request.phone,
        subject=inquiry_request.subject,
        message=inquiry_request.message
    )
    
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    
    # Generate AI response in background
    background_tasks.add_task(
        process_inquiry_with_ai,
        inquiry.id,
        inquiry_request.name,
        inquiry_request.email,
        inquiry_request.subject,
        inquiry_request.message
    )
    
    return InquiryResponse(
        inquiry_id=inquiry.id,
        status=inquiry.status,
        ai_response=None,
        response_sent=False
    )

async def process_inquiry_with_ai(
    inquiry_id: int,
    name: str,
    email: str,
    subject: str,
    message: str
):
    """Process inquiry with AI and send response"""
    
    db = SessionLocal()
    try:
        # Generate AI response
        ai_response = await generate_inquiry_response(subject, message)
        
        # Update inquiry with AI response
        inquiry = db.query(CustomerInquiry).filter(CustomerInquiry.id == inquiry_id).first()
        if inquiry:
            inquiry.ai_response = ai_response
            inquiry.status = "responded"
            inquiry.responded_at = datetime.utcnow()
            db.commit()
        
        # Send email response to customer
        await send_inquiry_response(
            email,
            name,
            subject,
            ai_response
        )
        
        # Send notification to spa manager
        await send_inquiry_response(
            settings.spa_manager_email,
            "Spa Manager",
            f"New Inquiry: {subject}",
            f"""
            New customer inquiry received:
            
            From: {name} ({email})
            Subject: {subject}
            Message: {message}
            
            AI Response: {ai_response}
            """,
            is_manager=True
        )
        
    except Exception as e:
        print(f"Error processing inquiry {inquiry_id}: {e}")
    finally:
        db.close()

@router.get("/inquiries/{inquiry_id}")
async def get_inquiry(inquiry_id: int, db: Session = Depends(get_db)):
    """Get inquiry details by ID"""
    
    inquiry = db.query(CustomerInquiry).filter(CustomerInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    return {
        "id": inquiry.id,
        "name": inquiry.name,
        "email": inquiry.email,
        "phone": inquiry.phone,
        "subject": inquiry.subject,
        "message": inquiry.message,
        "status": inquiry.status,
        "ai_response": inquiry.ai_response,
        "created_at": inquiry.created_at.isoformat(),
        "responded_at": inquiry.responded_at.isoformat() if inquiry.responded_at else None
    }

@router.get("/inquiries")
async def get_inquiries(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all inquiries with optional filtering"""
    
    query = db.query(CustomerInquiry)
    
    if status:
        query = query.filter(CustomerInquiry.status == status)
    
    inquiries = query.order_by(CustomerInquiry.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": inquiry.id,
            "name": inquiry.name,
            "email": inquiry.email,
            "subject": inquiry.subject,
            "status": inquiry.status,
            "created_at": inquiry.created_at.isoformat(),
            "responded_at": inquiry.responded_at.isoformat() if inquiry.responded_at else None
        }
        for inquiry in inquiries
    ]

@router.put("/inquiries/{inquiry_id}/status")
async def update_inquiry_status(
    inquiry_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update inquiry status"""
    
    if status not in ["new", "responded", "resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    inquiry = db.query(CustomerInquiry).filter(CustomerInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    inquiry.status = status
    if status == "resolved":
        inquiry.responded_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"Inquiry status updated to {status}"}

@router.post("/inquiries/{inquiry_id}/respond")
async def send_manual_response(
    inquiry_id: int,
    response_message: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send a manual response to an inquiry"""
    
    inquiry = db.query(CustomerInquiry).filter(CustomerInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    # Update inquiry
    inquiry.ai_response = response_message
    inquiry.status = "responded"
    inquiry.responded_at = datetime.utcnow()
    db.commit()
    
    # Send email response
    background_tasks.add_task(
        send_inquiry_response,
        inquiry.email,
        inquiry.name,
        inquiry.subject,
        response_message
    )
    
    return {"message": "Manual response sent successfully"}
