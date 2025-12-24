from pydantic import BaseModel, EmailStr
from datetime import datetime, date, time
from typing import Optional, List, Any

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str
    name: str
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    name: str
    phone: Optional[str]
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AppointmentTypeCreate(BaseModel):
    name: str
    duration_minutes: int
    matching_strategy: str
    max_days_ahead: int = 30
    is_online: bool = True
    config: Optional[Any] = None

class AppointmentTypeOut(AppointmentTypeCreate):
    id: int
    class Config: from_attributes = True

class AvailabilityCreate(BaseModel):
    provider_id: int
    date: date
    start_time: time
    end_time: time

class AppointmentBase(BaseModel):
    type_id: int
    seeker_id: int
    provider_id: int
    slot_id: int
    scheduled_time: datetime
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    seeker_name: str
    provider_name: str
    class Config:
        orm_mode = True

# Request schema
class ChatRequest(BaseModel):
    session_id: str
    input_text: str

# Response schema
class ChatResponse(BaseModel):
    session_id: str
    user_input: str
    llm_output: dict