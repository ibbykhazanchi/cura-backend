from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import models
import database
from database import engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Prescription Management API")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}/prescriptions", response_model=List[dict])
def get_user_prescriptions(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    prescriptions = db.query(models.Prescription).filter(
        models.Prescription.user_id == user_id
    ).all()
    
    return [
        {
            "id": p.id,
            "medication_name": p.medication_name,
            "dosage": p.dosage,
            "frequency": p.frequency,
            "start_date": p.start_date,
            "end_date": p.end_date,
            "notes": p.notes,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        }
        for p in prescriptions
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 