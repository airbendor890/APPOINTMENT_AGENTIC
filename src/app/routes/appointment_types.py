from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.post("/")
def create_appointment_type(type_data: dict, db: Session = Depends(get_db)):
    new_type = models.AppointmentType(**type_data)
    db.add(new_type)
    db.commit()
    db.refresh(new_type)
    return new_type

@router.get("/")
def list_appointment_types(db: Session = Depends(get_db)):
    return db.query(models.AppointmentType).all()
