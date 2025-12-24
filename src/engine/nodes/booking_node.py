from typing import Dict, Optional
from datetime import datetime
import sqlite3
from engine.state import AppointmentState, ConversationStage
from dao import DAOFactory
from datetime import datetime
from langgraph.prebuilt import ToolNode
from typing import Annotated
from langchain_core.tools import InjectedToolCallId
from langgraph.types import Command
from dao import Appointment
# Initialize DAO
dao_factory = DAOFactory()

from langchain_core.tools import tool



from dao import DAOFactory

##########################                   Tools for booking agent        ###################################################

# @tool
def book_slot_tool(seeker_id, provider_id, slot_id, scheduled_time, status, type_id=1, notes=None):
    """
    Book a new appointment slot for a seeker with a provider.

    Args:
        seeker_id (int): Unique identifier of the seeker (user/patient) booking the slot.
        provider_id (int): Unique identifier of the provider (doctor/mentor/etc.) with whom the slot is booked.
        slot_id (int): The ID of the availability slot being booked.
        scheduled_time (str): The scheduled appointment time (format: "YYYY-MM-DD HH:MM:SS").
        status (str): Status of the appointment (e.g., 'booked', 'pending', 'confirmed').
        type_id (int, optional): Type of appointment (default=1).
        notes (str, optional): Any additional notes related to the appointment.

    Returns:
        str | Appointment:
            - Returns an Appointment object with the generated appointment ID if successfully created.
            - Returns the string "error in creating appointment" if the insertion fails.

    Usage:
        >>> book_slot_tool(
        ...     seeker_id=101,
        ...     provider_id=55,
        ...     slot_id=3001,
        ...     scheduled_time="2025-09-10 14:30:00",
        ...     status="booked",
        ...     notes="First-time consultation"
        ... )
    """
    appointment_dao = dao_factory.get_appointment_dao()
    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    appointment = Appointment(
        type_id=type_id,
        seeker_id=seeker_id,
        provider_id=provider_id,
        slot_id=slot_id,
        scheduled_time=scheduled_time,
        status=status,
        notes=None,
        created_at=curr_time,
        updated_at=curr_time
    )

    try:
        appointment = appointment_dao.create(appointment)
    except Exception as e:
        return f"error in creating appointment for the slot id : {slot_id}. error : {e}"
    return appointment

# @tool
def cancel_slot_tool(appointment_id: int) -> dict:
    """
    Cancel an existing appointment slot.

    Args:
        appointment_id (int): The unique ID of the appointment to cancel.

    Returns:
        True if the appointment was successfully cancelled, otherwise False.

    Usage:
        - Use when the user explicitly requests to cancel an appointment.
        - Pass the `appointment_id` of the booking they want to cancel.
        - If the appointment exists, it will be marked as "cancelled".
    """
    appointment_dao = dao_factory.get_appointment_dao()
    result = appointment_dao.update(appointment_id, "cancelled")
    if result:
        return True
    else:
        return False    
# @tool
def update_slot_availability_tool(slot_id, status):
    """
    Update the availability status of a specific slot.
    Need to be called immediately after book_slot_tool with the booking info. need to mark the slot as booked.

    Args:
        slot_id (int): Unique identifier of the availability slot to update.
        status (str): New status for the slot (e.g., 'available', 'booked', 'blocked').

    Returns:
        bool | str:
            - Returns True if the slot status was successfully updated.
            - Returns False if no rows were updated (slot not found).
            - Returns an error string if the update operation fails.

    Usage:
        >>> update_slot_availability_tool(slot_id=3001, status="booked")
        True
    """
    availability_dao = dao_factory.get_availability_dao()
    try:
        availability_dao.update_slot_status(slot_id=slot_id, status=status)
    except:
        return f"error in updating slot status for slot id : {slot_id}"


# This node will handle calling your tool when Gemini requests it
# tools_node_scheduler = ToolNode([book_slot_tool,update_slot_availability_tool], messages_key="messages_history")





##--------------------------------------------------------------------
#                   NODE
##--------------------------------------------------------------------

from datetime import datetime

def booking_node(state: AppointmentState) -> AppointmentState:
    """
    Booking node that creates the appointment by invoking tools directly.
    Sequentially calls:
    1. book_slot_tool
    2. update_slot_availability_tool
    """

    print("\n\n booking agent : ")
    print(state["conversation_stage"])
    print(state)

    if state['conversation_stage'] == ConversationStage.CANCELLING:

        # cancel the slot now
        old_appointment_id = state['old_appointment']  # get the old appointment id from old_appointment
        old_slot_id = state['old_selected_slot'].get("slot_id") # get the old slot id from old_selected_slot

        try:
            res = cancel_slot_tool(old_appointment_id)
            print(f"cancelling old appointment {old_appointment_id} result: {res}")
        except Exception as e:
            print(f"Error cancelling old appointment {old_appointment_id}: {e}")

        # now update the old slot to available
        try:
            res = update_slot_availability_tool(old_slot_id, "available")
            print(f"updating old slot {old_slot_id} to available slot table: {res}")
        except Exception as e:
            print(f"Error updating old slot {old_slot_id} to available: {e}")

        confirmation_message = (
        f"  Your appointment has been Cancelled!\n"
        f"- Appointment ID: {old_appointment_id}\n"
                    )
        return {
            **state,
            "confirmation": confirmation_message,
            "conversation_stage": ConversationStage.CANCELLEATION_COMPLETE,
        }    
    
    selected_slot = state.get("selected_slot", {})
    seeker_contact = state.get("seeker_contact", {})

    if not selected_slot or not seeker_contact:
        return {
            **state,
            "error": "Missing information for booking",
            "conversation_stage": ConversationStage.BOOKING_COMPLETE
        }

    seeker_id = state.get("user_id", 5)
    provider_id = selected_slot.get("provider_id")
    slot_id = selected_slot.get("slot_id")
    date = selected_slot.get("date")          # e.g. "2025-08-30"
    start_time = selected_slot.get("start_time")  # e.g. "09:00:00"

    # Combine into proper timestamp
    scheduled_time = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S")

    # Book appointment
    appointment = book_slot_tool(
        seeker_id=seeker_id,
        provider_id=provider_id,
        slot_id=slot_id,
        scheduled_time=scheduled_time,
        status="booked",
        notes="Auto-booked via booking agent"
    )

    print(appointment)
    
    if isinstance(appointment, str) and appointment.startswith("error"):
        print(f"booking node :: appointment:: {appointment}")
        return {
            **state,
            "error": appointment,
            "conversation_stage": ConversationStage.BOOKING_COMPLETE
        }

    # Update slot availability
    slot_update = update_slot_availability_tool(slot_id=slot_id, status="booked")

    if isinstance(slot_update, str) and slot_update.startswith("error"):
        print(f"booking node :: slot update:: {slot_update}")
        return {
            **state,
            "error": slot_update,
            "conversation_stage": ConversationStage.BOOKING_COMPLETE
        }

    #Create confirmation message
    confirmation_message = (
        f"  Your appointment has been booked!\n"
        f"- Provider ID: {provider_id}\n"
        f'- Provider Name: {selected_slot.get("provider_name", "NA")}\n'
        f"- Scheduled Time: {scheduled_time}\n"
        f"- Appointment ID: {getattr(appointment, 'id', 'N/A')}"
    )

    if state.get('rescheduling_flag', False):

        # Cancel the old slot now
        old_appointment_id = state['old_appointment']  # get the old appointment id from old_appointment
        old_slot_id = state['old_selected_slot'].get("slot_id")  # get the old slot id from old_selected_slot

        try:
            cancel_slot_tool(old_appointment_id)
        except Exception as e:
            print(f"Error cancelling old appointment {old_appointment_id}: {e}")

        # now update the old slot to available
        try:
            update_slot_availability_tool(old_slot_id, "available")
        except Exception as e:
            print(f"Error updating old slot {old_slot_id} to available: {e}")

        confirmation_message = (
        f"  Your appointment has been Rescheduled!\n"
        f"- Provider ID: {provider_id}\n"
        f'- Provider Name: {selected_slot.get("provider_name", "NA")}\n'
        f"- Scheduled Time: {scheduled_time}\n"
        f"- Appointment ID: {getattr(appointment, 'id', 'N/A')}"
    )


    ## Send notification phone/email by using the tools

        ## If offline


        ## If online

    print(f"booking node :: confirmation message :: {confirmation_message}")
    return {
        **state,
        "appointment": appointment.id,
        "confirmation": confirmation_message,
        "conversation_stage": ConversationStage.BOOKING_COMPLETE,
    }

   
    
    


