from typing import List, Optional, TypedDict
from enum import Enum


class ConversationStage(Enum):

    INITIAL_REQUEST = "initial_request"

    GATHERING_SERVICE_INFO = "gathering_service_info" 
    GATHERING_TIME_PREFERENCES = "gathering_time_preferences"
    GATHERING_CONTACT_INFO = "gathering_contact_info"
    CONFIRMING_DETAILS = "confirming_details"
    
    # for communication with service_match agent
    PROCEED_TO_FETCH_SLOTS = "proceed_to_fetch_slots"
    SLOTS_FETCHED = "slots_fetched"
    NO_SERVICE_AVAILABLE = "no_service_available"
    NO_SLOT_AVAILABLE = "no_slot_available"
    CONFIRMING_SLOTS = "confirming_slots"
    
    # for communication with scheduler/booking agent
    PROCEED_TO_BOOKING = "proceed_to_booking"
    BOOKING_COMPLETE = "booking_complete"

    # for rescheduling/cancelling
    RESCHEDULING = "rescheduling"
    CANCELLING = "cancelling"
    CANCELLEATION_COMPLETE = "cancellation_complete"

class AppointmentState(TypedDict):

    #user details
    user_id: Optional[str]
    user_name: Optional[str]
    
    # Conversation Management
    conversation_stage: ConversationStage = ConversationStage.INITIAL_REQUEST
    messages_history: List[dict]          # Full conversation context among all, user, assistance as well as tools
    chat_history: List[dict]              # the conversation between AI and user that needs to be shown on the UI page
    missing_info: List[str]               # What we still need to collect
    
    # Information Collection (Incremental)
    seeker_request: str                   # Latest message
    service_info: Optional[dict]          # service_type, duration, special_requirements
    time_preferences: Optional[dict]      # preferred_date, preferred_time, flexibility
    seeker_contact: Optional[dict]        # name, email, phone
    location_preference: Optional[str]    # in-person vs online vs no-preference
    
    # AI Processing
    extracted_info: dict                  # Cumulative parsed information
    matched_providers: List[dict]         # Providers with required expertise
    available_slots: List[dict]           # Available time slots
    selected_slot: Optional[dict]         # Final booking choice SLOT
    old_selected_slot: Optional[dict]     # For rescheduling, the old slot to be cancelled

    rescheduling_flag: bool = False  # To indicate if the current flow is for rescheduling
    cancelling_flag: bool = False   # To indicate if the current flow is for cancelling
    booking_attempts: int                 # Number of attempts made to book the appointment

    # Final Booking
    appointment: Optional[int]
    old_appointment: Optional[int]        # For rescheduling/cancelling, the old appointment to be cancelled
    confirmation: Optional[str]          # Booking confirmation details
    meeting_info: Optional[dict]          # Google Meet link or location

    ## agent interaction loop counter