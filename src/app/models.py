from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, Time, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    preferences = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class AppointmentType(Base):
    __tablename__ = "appointment_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    matching_strategy = Column(String(50), nullable=False)
    max_days_ahead = Column(Integer, default=30)
    is_online = Column(Boolean, default=True)
    config = Column(JSONB)

class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(20), default="available")
    created_at = Column(TIMESTAMP, server_default=func.now())

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey("appointment_types.id"))
    seeker_id = Column(Integer, ForeignKey("users.id"))
    provider_id = Column(Integer, ForeignKey("users.id"))
    slot_id = Column(Integer, ForeignKey("availability_slots.id"))
    scheduled_time = Column(TIMESTAMP, nullable=False)
    status = Column(String(20), default="pending")
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
