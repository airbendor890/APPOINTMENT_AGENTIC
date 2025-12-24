from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, appointments, availability, appointment_types, chatbot

app = FastAPI(title="Appointment Scheduler API")

# allow all origins (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or ["http://localhost:3000", "http://192.168.1.23:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(availability.router, prefix="/availability", tags=["Availability"])
app.include_router(appointment_types.router, prefix="/types", tags=["Appointment Types"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])

@app.get("/")
def root():
    return {"message": "Appointment Scheduler API is running"}
