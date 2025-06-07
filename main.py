from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
import logging
from models import FrequencyType

import models
import database
from database import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Prescription Management API", debug=True)

# Pydantic models for request/response validation
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PrescriptionBase(BaseModel):
    medication_name: str
    dosage: str
    pills_per_dose: int
    frequency_type: FrequencyType
    frequency_value: int
    special_instructions: Optional[List[str]] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    prescription_metadata: Optional[Dict[str, Any]] = None

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionResponse(PrescriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User Management Endpoints
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Received request to create user with email: {user.email}")
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"Successfully created user with ID: {db_user.id}")
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserBase, db: Session = Depends(get_db)):
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
@app.post("/users/{user_id}/prescriptions/", response_model=PrescriptionResponse)
async def create_prescription(
    user_id: int,
    prescription: PrescriptionCreate,
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
        frequency_type=prescription.frequency_type,
        frequency_value=prescription.frequency_value,
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

@app.get("/users/{user_id}/prescriptions", response_model=List[PrescriptionResponse])
def get_user_prescriptions(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    prescriptions = db.query(models.Prescription).filter(
        models.Prescription.user_id == user_id
    ).all()
    
    return prescriptions

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 