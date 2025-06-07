from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PrescriptionBase(BaseModel):
    medication_name: str
    dosage: str
    pills_per_dose: int
    times_per_day: int
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

class UsageBase(BaseModel):
    prescription_id: int
    taken_at: datetime

class UsageCreate(UsageBase):
    pass

class UsageResponse(UsageBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 