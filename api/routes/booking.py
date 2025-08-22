from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import uuid

from core.database import get_db, Booking, Service
from services.email_service import send_booking_confirmation
from services.google_calendar import add_to_calendar
from services.google_sheets import add_booking_to_sheet
from core.config import settings

router = APIRouter()

class BookingRequest(BaseModel):
    client_name: str
    client_email: str
    client_phone: str
    service_name: str
    appointment_date: str  # YYYY-MM-DD format
    appointment_time: str  # HH:MM format
    special_requests: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: int
    confirmation_code: str
    appointment_datetime: str
    service_name: str
    total_price: float
    status: str

@router.post("/book", response_model=BookingResponse)
async def create_booking(
    booking_request: BookingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new spa booking with full automation"""
    
    # Validate service exists
    service = db.query(Service).filter(
        Service.name == booking_request.service_name,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Parse appointment datetime
    try:
        appointment_datetime = datetime.strptime(
            f"{booking_request.appointment_date} {booking_request.appointment_time}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date/time format")
    
    # Check if appointment is in the future
    if appointment_datetime <= datetime.now():
        raise HTTPException(status_code=400, detail="Appointment must be in the future")
    
    # Check business hours
    day_of_week = appointment_datetime.strftime("%A").lower()
    if day_of_week not in settings.business_hours:
        raise HTTPException(status_code=400, detail="Spa is closed on this day")
    
    business_hours = settings.business_hours[day_of_week]
    appointment_time = appointment_datetime.strftime("%H:%M")
    
    if appointment_time < business_hours["open"] or appointment_time > business_hours["close"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Spa is open from {business_hours['open']} to {business_hours['close']} on {day_of_week}"
        )
    
    # Check for conflicting bookings
    end_time = appointment_datetime + timedelta(minutes=service.duration)
    conflicting_booking = db.query(Booking).filter(
        Booking.appointment_date == appointment_datetime.date(),
        Booking.status == "confirmed",
        Booking.appointment_time.between(
            appointment_datetime.strftime("%H:%M"),
            end_time.strftime("%H:%M")
        )
    ).first()
    
    if conflicting_booking:
        raise HTTPException(status_code=409, detail="Time slot is already booked")
    
    # Create booking
    confirmation_code = str(uuid.uuid4())[:8].upper()
    
    booking = Booking(
        client_name=booking_request.client_name,
        client_email=booking_request.client_email,
        client_phone=booking_request.client_phone,
        service_name=service.name,
        service_duration=service.duration,
        appointment_date=appointment_datetime,
        appointment_time=appointment_datetime.strftime("%H:%M"),
        total_price=service.price,
        special_requests=booking_request.special_requests
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    # Background tasks for automation
    background_tasks.add_task(
        send_booking_confirmation,
        booking_request.client_email,
        booking_request.client_name,
        service.name,
        appointment_datetime,
        service.price,
        confirmation_code
    )
    
    background_tasks.add_task(
        send_booking_confirmation,
        settings.spa_manager_email,
        "Spa Manager",
        service.name,
        appointment_datetime,
        service.price,
        confirmation_code,
        is_manager=True,
        client_details=booking_request
    )
    
    # Add to Google Calendar
    try:
        calendar_event_id = await add_to_calendar(
            booking_request.client_name,
            service.name,
            appointment_datetime,
            service.duration,
            booking_request.client_email
        )
        booking.google_calendar_event_id = calendar_event_id
        db.commit()
    except Exception as e:
        print(f"Warning: Could not add to Google Calendar: {e}")
    
    # Add to Google Sheets
    try:
        await add_booking_to_sheet(booking)
    except Exception as e:
        print(f"Warning: Could not add to Google Sheets: {e}")
    
    return BookingResponse(
        booking_id=booking.id,
        confirmation_code=confirmation_code,
        appointment_datetime=appointment_datetime.isoformat(),
        service_name=service.name,
        total_price=service.price,
        status=booking.status
    )

@router.get("/bookings/{booking_id}")
async def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """Get booking details by ID"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {
        "id": booking.id,
        "client_name": booking.client_name,
        "client_email": booking.client_email,
        "service_name": booking.service_name,
        "appointment_date": booking.appointment_date.isoformat(),
        "appointment_time": booking.appointment_time,
        "total_price": booking.total_price,
        "status": booking.status,
        "created_at": booking.created_at.isoformat()
    }

@router.get("/available-slots")
async def get_available_slots(
    date: str,  # YYYY-MM-DD format
    service_name: str,
    db: Session = Depends(get_db)
):
    """Get available time slots for a specific date and service"""
    
    # Get service details
    service = db.query(Service).filter(
        Service.name == service_name,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Parse date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Check business hours
    day_of_week = target_date.strftime("%A").lower()
    if day_of_week not in settings.business_hours:
        return {"available_slots": []}
    
    business_hours = settings.business_hours[day_of_week]
    
    # Generate time slots
    start_time = datetime.strptime(business_hours["open"], "%H:%M").time()
    end_time = datetime.strptime(business_hours["close"], "%H:%M").time()
    
    # Get existing bookings for this date
    existing_bookings = db.query(Booking).filter(
        Booking.appointment_date == target_date,
        Booking.status == "confirmed"
    ).all()
    
    booked_times = set()
    for booking in existing_bookings:
        booking_start = datetime.strptime(booking.appointment_time, "%H:%M").time()
        booking_end = (
            datetime.strptime(booking.appointment_time, "%H:%M") + 
            timedelta(minutes=booking.service_duration)
        ).time()
        
        # Add all times in this booking slot
        current_time = booking_start
        while current_time < booking_end:
            booked_times.add(current_time.strftime("%H:%M"))
            current_time = (
                datetime.combine(datetime.min, current_time) + 
                timedelta(minutes=15)
            ).time()
    
    # Generate available slots
    available_slots = []
    current_time = start_time
    
    while current_time <= end_time:
        slot_end = (
            datetime.combine(datetime.min, current_time) + 
            timedelta(minutes=service.duration)
        ).time()
        
        if slot_end <= end_time:
            # Check if this slot is available
            is_available = True
            check_time = current_time
            
            while check_time < slot_end:
                if check_time.strftime("%H:%M") in booked_times:
                    is_available = False
                    break
                check_time = (
                    datetime.combine(datetime.min, check_time) + 
                    timedelta(minutes=15)
                ).time()
            
            if is_available:
                available_slots.append(current_time.strftime("%H:%M"))
        
        current_time = (
            datetime.combine(datetime.min, current_time) + 
            timedelta(minutes=settings.buffer_time + 15)
        ).time()
    
    return {"available_slots": available_slots}
