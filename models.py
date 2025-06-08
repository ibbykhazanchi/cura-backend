from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    prescriptions = relationship("Prescription", back_populates="user")
    usage_logs = relationship("Usage", back_populates="user")
    check_ins = relationship("CheckIn", back_populates="user")

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    medication_name = Column(String, index=True)
    dosage = Column(String)
    pills_per_dose = Column(Integer)
    times_per_day = Column(Integer)  # Number of times per day (1 = once daily, 2 = twice daily, etc.)
    special_instructions = Column(JSON)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    prescription_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    user = relationship("User", back_populates="prescriptions")
    usage_logs = relationship("Usage", back_populates="prescription")

class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"))
    taken_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="usage_logs")
    prescription = relationship("Prescription", back_populates="usage_logs")

class CheckIn(Base):
    __tablename__ = "check_ins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.now(timezone.utc))
    transcript = Column(Text)
    side_effects = Column(JSON)  # List of strings
    red_flags = Column(JSON)     # List of strings
    mood = Column(Integer)       # 1-10 scale
    clinical_effectiveness = Column(JSON)  # List of strings
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="check_ins") 