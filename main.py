from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import logging
import httpx
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import models
import database
from database import engine
import schemas
import adherence

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Prescription Management API", debug=True)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User Management Endpoints
@app.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Received request to create user with email: {user.email}")
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"Successfully created user with ID: {db_user.id}")
    return db_user

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if new email is already taken by another user
    if user.email != db_user.email:
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Update user fields
    db_user.email = user.email
    db_user.full_name = user.full_name
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

# Prescription Endpoints
@app.post("/users/{user_id}/prescriptions/", response_model=schemas.PrescriptionResponse)
async def create_prescription(
    user_id: int,
    prescription: schemas.PrescriptionCreate,
    db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create new prescription
    db_prescription = models.Prescription(
        user_id=user_id,
        medication_name=prescription.medication_name,
        dosage=prescription.dosage,
        pills_per_dose=prescription.pills_per_dose,
        times_per_day=prescription.times_per_day,
        special_instructions=prescription.special_instructions,
        start_date=prescription.start_date,
        end_date=prescription.end_date,
        prescription_metadata=prescription.prescription_metadata
    )
    
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    logger.info(f"Successfully created prescription with ID: {db_prescription.id} for user: {user_id}")
    return db_prescription

@app.get("/users/{user_id}/prescriptions", response_model=List[schemas.PrescriptionResponse])
def get_user_prescriptions(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    prescriptions = db.query(models.Prescription).filter(
        models.Prescription.user_id == user_id
    ).all()
    
    return prescriptions

# Usage Endpoints
@app.post("/users/{user_id}/usage/", response_model=schemas.UsageResponse)
async def log_usage(
    user_id: int,
    usage: schemas.UsageCreate,
    db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if prescription exists and belongs to user
    db_prescription = db.query(models.Prescription).filter(
        models.Prescription.id == usage.prescription_id,
        models.Prescription.user_id == user_id
    ).first()
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found or does not belong to user")
    
    # Create usage log
    db_usage = models.Usage(
        user_id=user_id,
        prescription_id=usage.prescription_id,
        taken_at=usage.taken_at
    )
    
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)
    logger.info(f"Successfully logged usage for prescription {usage.prescription_id} by user {user_id}")
    return db_usage

@app.get("/users/{user_id}/usage/", response_model=List[schemas.UsageResponse])
def get_user_usage(
    user_id: int,
    prescription_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query
    query = db.query(models.Usage).filter(models.Usage.user_id == user_id)
    
    # Apply prescription filter if provided
    if prescription_id:
        # Check if prescription exists and belongs to user
        db_prescription = db.query(models.Prescription).filter(
            models.Prescription.id == prescription_id,
            models.Prescription.user_id == user_id
        ).first()
        if db_prescription is None:
            raise HTTPException(status_code=404, detail="Prescription not found or does not belong to user")
        query = query.filter(models.Usage.prescription_id == prescription_id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(models.Usage.taken_at >= start_date)
    if end_date:
        query = query.filter(models.Usage.taken_at <= end_date)
    
    # Order by taken_at descending
    query = query.order_by(models.Usage.taken_at.desc())
    
    return query.all()

@app.get("/users/{user_id}/prescriptions/{prescription_id}/adherence", response_model=dict)
def get_prescription_adherence(
    user_id: int,
    prescription_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    late_threshold_hours: Optional[int] = 2,
    db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get prescription
    db_prescription = db.query(models.Prescription).filter(
        models.Prescription.id == prescription_id,
        models.Prescription.user_id == user_id
    ).first()
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found or does not belong to user")
    
    # Get usage logs for this prescription
    usage_logs = db.query(models.Usage).filter(
        models.Usage.user_id == user_id,
        models.Usage.prescription_id == prescription_id
    ).all()
    
    # Calculate adherence
    result = adherence.calculate_adherence(
        prescription=db_prescription,
        usage_logs=usage_logs,
        start_date=start_date,
        end_date=end_date,
        late_threshold_hours=late_threshold_hours
    )
    
    # Convert result to dictionary
    return {
        "total_expected_doses": result.total_expected_doses,
        "total_taken_doses": result.total_taken_doses,
        "missed_doses": result.missed_doses,
        "late_doses": result.late_doses,
        "missed_dates": [d.isoformat() for d in result.missed_dates],
        "late_dates": [d.isoformat() for d in result.late_dates],
        "details": result.details
    }

# Check-in Endpoints
@app.post("/users/{user_id}/check-ins/", response_model=schemas.CheckInResponse)
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

@app.get("/users/{user_id}/check-ins/", response_model=List[schemas.CheckInResponse])
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

@app.get("/users/{user_id}/check-ins/{check_in_id}", response_model=schemas.CheckInResponse)
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

@app.get("/session")
async def get_session():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/realtime/sessions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-realtime-preview-2025-06-03",
                "voice": "verse",
            }
        )
        return response.json()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 