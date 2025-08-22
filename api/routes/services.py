from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from core.database import get_db, Service
from core.config import settings

router = APIRouter()

class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str
    duration: int
    price: float
    category: str
    is_active: bool

class ServiceCategory(BaseModel):
    category: str
    services: List[ServiceResponse]

@router.get("/services", response_model=List[ServiceResponse])
async def get_services(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all available spa services, optionally filtered by category"""
    
    query = db.query(Service).filter(Service.is_active == True)
    
    if category:
        query = query.filter(Service.category == category)
    
    services = query.order_by(Service.category, Service.name).all()
    
    return [
        ServiceResponse(
            id=service.id,
            name=service.name,
            description=service.description,
            duration=service.duration,
            price=service.price,
            category=service.category,
            is_active=service.is_active
        )
        for service in services
    ]

@router.get("/services/categories", response_model=List[ServiceCategory])
async def get_services_by_category(db: Session = Depends(get_db)):
    """Get services grouped by category"""
    
    services = db.query(Service).filter(Service.is_active == True).order_by(Service.category, Service.name).all()
    
    # Group by category
    categories = {}
    for service in services:
        if service.category not in categories:
            categories[service.category] = []
        
        categories[service.category].append(
            ServiceResponse(
                id=service.id,
                name=service.name,
                description=service.description,
                duration=service.duration,
                price=service.price,
                category=service.category,
                is_active=service.is_active
            )
        )
    
    return [
        ServiceCategory(category=category, services=services_list)
        for category, services_list in categories.items()
    ]

@router.get("/services/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    """Get a specific service by ID"""
    
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return ServiceResponse(
        id=service.id,
        name=service.name,
        description=service.description,
        duration=service.duration,
        price=service.price,
        category=service.category,
        is_active=service.is_active
    )

@router.get("/services/search/{search_term}")
async def search_services(search_term: str, db: Session = Depends(get_db)):
    """Search services by name or description"""
    
    services = db.query(Service).filter(
        Service.is_active == True,
        (Service.name.ilike(f"%{search_term}%") | Service.description.ilike(f"%{search_term}%"))
    ).all()
    
    return [
        ServiceResponse(
            id=service.id,
            name=service.name,
            description=service.description,
            duration=service.duration,
            price=service.price,
            category=service.category,
            is_active=service.is_active
        )
        for service in services
    ]

@router.get("/services/popular")
async def get_popular_services(db: Session = Depends(get_db)):
    """Get popular services (can be customized based on booking frequency)"""
    
    # For now, return services with higher prices as "popular"
    # In a real system, this would be based on actual booking data
    popular_services = db.query(Service).filter(
        Service.is_active == True
    ).order_by(Service.price.desc()).limit(5).all()
    
    return [
        ServiceResponse(
            id=service.id,
            name=service.name,
            description=service.description,
            duration=service.duration,
            price=service.price,
            category=service.category,
            is_active=service.is_active
        )
        for service in popular_services
    ]

@router.get("/services/recommendations")
async def get_service_recommendations(
    category: Optional[str] = None,
    max_duration: Optional[int] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get personalized service recommendations"""
    
    query = db.query(Service).filter(Service.is_active == True)
    
    if category:
        query = query.filter(Service.category == category)
    
    if max_duration:
        query = query.filter(Service.duration <= max_duration)
    
    if max_price:
        query = query.filter(Service.price <= max_price)
    
    # Sort by best value (price per minute)
    services = query.all()
    services_with_value = []
    
    for service in services:
        value_score = service.price / service.duration
        services_with_value.append((service, value_score))
    
    # Sort by value score (lower is better)
    services_with_value.sort(key=lambda x: x[1])
    
    return [
        ServiceResponse(
            id=service.id,
            name=service.name,
            description=service.description,
            duration=service.duration,
            price=service.price,
            category=service.category,
            is_active=service.is_active
        )
        for service, _ in services_with_value[:5]  # Return top 5 recommendations
    ]
