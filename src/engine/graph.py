from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from .state import AppointmentState
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from engine.nodes import information_gatherer_node, service_matcher_node, booking_node, conversation_router, tools_node_matcher, matcher_tool_result_handler
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver


db_path = "state_db/example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)

memory = SqliteSaver(conn)

def create_appointment_graph():
    """
    Creates the main appointment booking graph
    """
    
    # Create the graph
    workflow = StateGraph(AppointmentState)
    
    # Add nodes
    workflow.add_node("gather_info_agent", information_gatherer_node)
    workflow.add_node("match_services_agent", service_matcher_node)
    workflow.add_node("scheduler_agent", booking_node)


    # Tool nodes
    workflow.add_node("tools_node_matcher", tools_node_matcher)
    workflow.add_node("matcher_tool_result_handler", matcher_tool_result_handler)
    # workflow.add_node("tools_node_scheduler", tools_node_scheduler)
    # workflow.add_node("booking_tool_result_handler", booking_tool_result_handler)

    # Add conditional routing
    workflow.add_conditional_edges(
        "gather_info_agent",
        conversation_router,
        {   
            "gather_info": END,
            "match_services": "match_services_agent", # Move to service matching
            "schedule": "scheduler_agent", # Move to scheduler agent
            "end": END
        }
    )


    ## custom tool condition
    def custom_tool_condition(state):
        ai_message = state["messages_history"][-1] 
        print(isinstance(ai_message, AIMessage))
        print(ai_message)
        return tools_condition(state, messages_key="messages_history")

    ## for match_services_agent----------------- 

    workflow.add_conditional_edges(
    "match_services_agent",
    custom_tool_condition,
    {
        "tools": "tools_node_matcher",      
        "__end__": "matcher_tool_result_handler"
    },
    )
    # After tool execution → return to matcher or next stage
    workflow.add_edge("tools_node_matcher", "match_services_agent")
    workflow.add_edge("matcher_tool_result_handler", "gather_info_agent")
    # Sequential flow after info gathering
    # workflow.add_edge("matcher_tool_result_handler", "gather_info_agent")



    workflow.add_edge("scheduler_agent", "gather_info_agent")

    
    # Set entry point
    workflow.set_entry_point("gather_info_agent")
    
    return workflow.compile(checkpointer=memory)

if __name__ == '__main__':
    graph = create_appointment_graph()