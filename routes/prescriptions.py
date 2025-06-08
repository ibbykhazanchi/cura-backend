from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/users/{user_id}/prescriptions",
    tags=["prescriptions"]
)

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.PrescriptionResponse)
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

@router.get("", response_model=List[schemas.PrescriptionResponse])
def get_user_prescriptions(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    prescriptions = db.query(models.Prescription).filter(
        models.Prescription.user_id == user_id
    ).all()
    
    return prescriptions 