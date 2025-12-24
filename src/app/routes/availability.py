from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.post("/")
def create_availability(slot: dict, db: Session = Depends(get_db)):
    new_slot = models.AvailabilitySlot(**slot)
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    return new_slot
