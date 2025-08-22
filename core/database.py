from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from core.config import settings

# Database setup
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False)
    client_phone = Column(String, nullable=False)
    service_name = Column(String, nullable=False)
    service_duration = Column(Integer, nullable=False)  # minutes
    appointment_date = Column(DateTime, nullable=False)
    appointment_time = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="confirmed")  # confirmed, completed, cancelled
    special_requests = Column(Text, nullable=True)
    google_calendar_event_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CustomerInquiry(Base):
    __tablename__ = "customer_inquiries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String, default="new")  # new, responded, resolved
    ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=False)
    duration = Column(Integer, nullable=False)  # minutes
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # massage, facial, body treatment, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, unique=True)
    user_email = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    is_user_message = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables and default data"""
    Base.metadata.create_all(bind=engine)
    
    # Add default services if they don't exist
    db = SessionLocal()
    try:
        default_services = [
            {
                "name": "Swedish Massage",
                "description": "Relaxing full-body massage using long, flowing strokes",
                "duration": 60,
                "price": 80.00,
                "category": "massage"
            },
            {
                "name": "Deep Tissue Massage",
                "description": "Therapeutic massage targeting deep muscle layers",
                "duration": 60,
                "price": 90.00,
                "category": "massage"
            },
            {
                "name": "Hot Stone Massage",
                "description": "Massage with heated stones for ultimate relaxation",
                "duration": 75,
                "price": 110.00,
                "category": "massage"
            },
            {
                "name": "Classic Facial",
                "description": "Cleansing, exfoliating, and nourishing facial treatment",
                "duration": 60,
                "price": 70.00,
                "category": "facial"
            },
            {
                "name": "Anti-Aging Facial",
                "description": "Advanced facial with anti-aging ingredients",
                "duration": 75,
                "price": 95.00,
                "category": "facial"
            },
            {
                "name": "Body Scrub",
                "description": "Exfoliating body treatment with natural ingredients",
                "duration": 45,
                "price": 65.00,
                "category": "body_treatment"
            },
            {
                "name": "Aromatherapy Session",
                "description": "Therapeutic session using essential oils",
                "duration": 60,
                "price": 85.00,
                "category": "wellness"
            }
        ]
        
        for service_data in default_services:
            existing_service = db.query(Service).filter(Service.name == service_data["name"]).first()
            if not existing_service:
                service = Service(**service_data)
                db.add(service)
        
        db.commit()
        print("✅ Database initialized with default services")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
