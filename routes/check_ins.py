from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import logging

import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/users/{user_id}/check-ins",
    tags=["check-ins"]
)

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.CheckInResponse)
async def create_check_in(
    user_id: int,
    check_in: schemas.CheckInCreate,
    db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create new check-in
    db_check_in = models.CheckIn(
        user_id=user_id,
        transcript=check_in.transcript,
        side_effects=check_in.side_effects,
        red_flags=check_in.red_flags,
        mood=check_in.mood,
        clinical_effectiveness=check_in.clinical_effectiveness,
        date=check_in.date or datetime.now(timezone.utc)
    )
    
    db.add(db_check_in)
    db.commit()
    db.refresh(db_check_in)
    logger.info(f"Successfully created check-in with ID: {db_check_in.id} for user: {user_id}")
    return db_check_in

@router.get("/", response_model=List[schemas.CheckInResponse])
def get_user_check_ins(
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query
    query = db.query(models.CheckIn).filter(models.CheckIn.user_id == user_id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(models.CheckIn.date >= start_date)
    if end_date:
        query = query.filter(models.CheckIn.date <= end_date)
    
    # Order by date descending
    query = query.order_by(models.CheckIn.date.desc())
    
    return query.all()

@router.get("/{check_in_id}", response_model=schemas.CheckInResponse)
def get_check_in(
    user_id: int,
    check_in_id: int,
    db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get check-in
    db_check_in = db.query(models.CheckIn).filter(
        models.CheckIn.id == check_in_id,
        models.CheckIn.user_id == user_id
    ).first()
    
    if db_check_in is None:
        raise HTTPException(status_code=404, detail="Check-in not found")
    
    return db_check_in 