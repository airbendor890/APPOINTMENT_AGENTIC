from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, aliased
from .. import models, schemas
from ..deps import get_db, get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=schemas.AppointmentResponse)
def create_appointment(appointment: schemas.AppointmentBase, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_appt = models.Appointment(**appointment.dict(), status="pending")
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    return db_appt

@router.get("/me/upcoming", response_model=list[schemas.AppointmentResponse])
def get_upcoming_appointments(db: Session = Depends(get_db), user=Depends(get_current_user)):

    Seeker = aliased(models.User)
    Provider = aliased(models.User)

    results = (
        db.query(
            models.Appointment,
            Seeker.name.label("seeker_name"),
            Provider.name.label("provider_name"),
        )
        .join(Seeker, Seeker.id == models.Appointment.seeker_id)
        .join(Provider, Provider.id == models.Appointment.provider_id)
        .filter(
            (models.Appointment.seeker_id == user.id) |
            (models.Appointment.provider_id == user.id),
            models.Appointment.scheduled_time > datetime.utcnow(),
        )
        .all()
    )

    # Need to massage result into dicts for Pydantic
    return [
        {
            **a.__dict__,
            "seeker_name": seeker_name,
            "provider_name": provider_name
        }
        for a, seeker_name, provider_name in results
    ]

@router.get("/me/past", response_model=list[schemas.AppointmentResponse])
def get_past_appointments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    Seeker = aliased(models.User)
    Provider = aliased(models.User)

    results = (
        db.query(
            models.Appointment,
            Seeker.name.label("seeker_name"),
            Provider.name.label("provider_name"),
        )
        .join(Seeker, Seeker.id == models.Appointment.seeker_id)
        .join(Provider, Provider.id == models.Appointment.provider_id)
        .filter(
            (models.Appointment.seeker_id == user.id) |
            (models.Appointment.provider_id == user.id),
            models.Appointment.scheduled_time < datetime.utcnow(),
        )
        .all()
    )

    # Need to massage result into dicts for Pydantic
    return [
        {
            **a.__dict__,
            "seeker_name": seeker_name,
            "provider_name": provider_name
        }
        for a, seeker_name, provider_name in results
    ]


@router.delete("/{appointment_id}")
def delete_upcoming_appointment(appointment_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appt.scheduled_time < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Cannot delete past appointments")
    if appt.seeker_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(appt)
    db.commit()
    return {"message": "Appointment deleted"}
