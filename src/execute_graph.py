from engine.graph import create_appointment_graph


graph = create_appointment_graph()

def execute_chat(input_dict):
    response = graph.invoke(input_dict, config={"configurable": {"thread_id": "101"}})
    return response