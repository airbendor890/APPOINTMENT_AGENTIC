from engine.state import AppointmentState, ConversationStage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict
import sqlite3
from datetime import datetime, timedelta

from langgraph.prebuilt import ToolNode
from typing import Annotated
from langchain_core.tools import InjectedToolCallId
from langgraph.types import Command
from dao import DAOFactory
from dao import Appointment
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

# Initialize DAO
dao_factory = DAOFactory()



###############################   Tools for slot/service matching agent ################################### 
@tool
def find_available_slots_by_date_overlapping_time_range_tool(
    tool_call_id: Annotated[str, InjectedToolCallId],
    date: str,
    start_time: str,
    end_time: str = None,
    status: str = "available",
    service_name: str = None,
):
    """
    Find available time slots by date and overlapping time range.

    Args:
        date (str): The date in YYYY-MM-DD format.
        start_time (str): Start time in HH:MM format.
        end_time (str, optional): End time in HH:MM format. If not provided, defaults to +1 hour.
        status (str, optional): Slot status to filter by (default "available").
        service_name (str, optional): Filter by service name (case-insensitive, partial match).

    Returns:
        Command: Updates state with available slots, conversation stage, and a ToolMessage.
    """

    availability_dao = dao_factory.get_availability_dao()

    try:
        availability_slots = availability_dao.get_slots_by_date_overlapping_time_range(
            date, start_time, end_time, status, service_name
        )
    except Exception as e:
        print("availability error:", e)
        availability_slots = None

    if availability_slots:
        conv_stage = ConversationStage.SLOTS_FETCHED
        msg_text = f"Found {len(availability_slots)} slots: {availability_slots}"
    else:
        conv_stage = ConversationStage.NO_SLOT_AVAILABLE
        msg_text = "No available slots found."

    print("tool node - call - available slots:", availability_slots)

    return Command(
        update={
            "available_slots": availability_slots,
            "conversation_stage": conv_stage,
            "messages_history": [
                ToolMessage(
                    content=msg_text,
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


# This node will handle calling your tool when Gemini requests it
tools_node_matcher = ToolNode([find_available_slots_by_date_overlapping_time_range_tool], messages_key="messages_history")

def matcher_tool_result_handler(state: AppointmentState):
    if state.get("conversation_stage") == ConversationStage.PROCEED_TO_FETCH_SLOTS:
        return {
            **state,    
            "available_slots": [],
            "conversation_stage": ConversationStage.NO_SLOT_AVAILABLE
        }
    else:
        return state

##--------------------------------------------------------------------
#                   NODE
##--------------------------------------------------------------------


def service_matcher_node(state: AppointmentState):

    # print(state)
    print("\n\n service matcher agent : ")
    print(state["conversation_stage"])

    service_info = state.get("service_info", {})
    time_preferences = state.get("time_preferences", {})
    location_preference = state.get("location_preference", "no-preference")

    slots_prompt = f"""
    You are an agent whose job is to find available slots based on their preferences:

    - Service info: {service_info}
    - Time preferences: {time_preferences}
    - Location preference: {location_preference}


    - messages history : {state['messages_history']}


    Look at the **last message** in messages_history.
    - If it contains a tool call to `find_available_slots_by_date_overlapping_time_range_tool`,
        then check the tool's result (available slots).
    - If slots were found (non-empty), output `_end_`.
    - If slots were not found (empty list), output `_end_`.
    - Do **not** call the tool again in these cases.

    """

    llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0).bind_tools([find_available_slots_by_date_overlapping_time_range_tool])

    result = llm.invoke(slots_prompt)

    print(type(result))
    print(result)

    
    return {
        **state,
        "messages_history": state.get("messages_history", []) + [result]
    }


