from engine.state import AppointmentState, ConversationStage

####-----------------------------------------------------------------------
#                       ROUTER
####-----------------------------------------------------------------------


# Conditional routing function for LangGraph
def conversation_router(state: AppointmentState) -> str:
    """
    Main routing function for the graph
    """
    stage = state.get("conversation_stage", ConversationStage.INITIAL_REQUEST)
    missing_info = state.get("missing_info", [])
    
    # If we still have missing required info, continue gathering
    if missing_info:
        return "gather_info"
    
    # If we have all info, move to next stage
    if stage == ConversationStage.PROCEED_TO_FETCH_SLOTS:
        return "match_services"
    
    if stage == ConversationStage.SLOTS_FETCHED:
        return "end"
    
    if stage == ConversationStage.PROCEED_TO_BOOKING:
        return "schedule"
    
    if stage == ConversationStage.CANCELLING:
        return "schedule"
    # If booking is complete
    if stage == ConversationStage.BOOKING_COMPLETE:
        return "end"
    
    # Default: gather more info
    return "gather_info"