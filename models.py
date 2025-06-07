from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import enum

Base = declarative_base()

class FrequencyType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    prescriptions = relationship("Prescription", back_populates="user")

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    medication_name = Column(String, index=True)
    dosage = Column(String)
    pills_per_dose = Column(Integer)
    frequency_type = Column(Enum(FrequencyType))
    frequency_value = Column(Integer)
    special_instructions = Column(JSON)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    prescription_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    user = relationship("User", back_populates="prescriptions") 