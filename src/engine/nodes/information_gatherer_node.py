from engine.state import AppointmentState, ConversationStage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv, find_dotenv
import json
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict
from dao import DAOFactory

_ = load_dotenv(find_dotenv())



##--------------------------------------------------------------------
#                   NODE
##--------------------------------------------------------------------
def information_gatherer_node(state: AppointmentState) -> AppointmentState:
    """
    Main node that handles conversation flow and information collection ((Communication agent)
    """
    # print(state)
    print("\n\nCommunication agent : ")
    print(state["conversation_stage"])

### --------------------------------------   for information gather, communication with seeker ---------------------------------------
    
    if state['conversation_stage'] in [ConversationStage.INITIAL_REQUEST, ConversationStage.CONFIRMING_DETAILS, ConversationStage.GATHERING_CONTACT_INFO,\
                                       ConversationStage.GATHERING_SERVICE_INFO, ConversationStage.GATHERING_TIME_PREFERENCES]:
        # Initialize Gemini model
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                temperature=0,
                                max_tokens=None,
                                timeout=None,
                                max_retries=2)
        
        # Check what information we still need
        missing_info = identify_missing_information(state)
        print("Missing Info: ", missing_info)
        # if not missing_info:
        #     # All required info collected, move to next stage
        #     return {
        #         **state,
        #         "conversation_stage": ConversationStage.PROCEED_TO_FETCH_SLOTS,
        #         "missing_info": []
        #     }
        
        # Extract any new information from the latest message
        extracted_info = extract_information_from_message(state["seeker_request"], llm, state['conversation_stage'])

        print("Extracted Info: ", extracted_info)
        
        # Update state with newly extracted info
        updated_state = update_state_with_extracted_info(state, extracted_info)
        
        # Re-check missing info after extraction
        remaining_missing = identify_missing_information(updated_state)
        print("Remaining State: ", remaining_missing)
        
        if not remaining_missing:
            available_services = DAOFactory().get_service_dao().get_all_service_names()
            print("Available Services: ", available_services)
            # Check if the extracted service type is valid
            if updated_state.get("service_info", {}).get("service_type") is None or updated_state.get("service_info", {}).get("service_type") == "null" or updated_state.get("service_info", {}).get("service_type") not in available_services:
                # No matching service found, inform user
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    temperature=0.3,
                    max_retries=2
                )   
                prompt = f"""
                You are a friendly appointment booking assistant.  
                The user requested a service type that we do not offer: {updated_state.get('service_info', {}).get('service_type')}.  
                Our available services are: {', '.join(available_services)}.  
                Inform the user politely that we do not offer the requested service and ask them to specify a different one.
                Keep the tone polite and conversational.
                """

                response = llm.invoke(prompt)
                follow_up_message = response.content.strip()        
                
                new_messages_history = updated_state.get("messages_history", []).copy()
                new_chat_history =  updated_state.get("chat_history", []).copy()       
                new_messages_history.extend([
                    {"role": "user", "content": state["seeker_request"]},
                    {"role": "assistant", "content": follow_up_message}
                ])
                new_chat_history.extend([
                    {"role": "user", "content": state["seeker_request"],"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                    {"role": "assistant", "content": follow_up_message, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                ])

                return {
                    **updated_state,
                    "messages_history": new_messages_history,
                    "chat_history": new_chat_history,
                    "conversation_stage": ConversationStage.GATHERING_SERVICE_INFO,
                    "missing_info": []
                }
            # All info now complete --> proceed to fetch slots

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",   
                temperature=0.3,
                max_retries=2
            )       
            prompt = f"""
            You are a friendly appointment booking assistant.  
            The user has provided all necessary information for booking an appointment:
            - Service type: {updated_state.get('service_info', {}).get('service_type')}
            - Preferred date: {updated_state.get('time_preferences', {}).get('preferred_date')}  

                        Confirm with the user that you will now check for available slots based on their preferences.
            Keep the tone polite and conversational. 
            Here is the chat history for context:
            { ' | '.join([msg["content"] for msg in state.get("chat_history", [])]) }
            """

            follow_up_message = llm.invoke(prompt).content.strip()  

            new_messages_history = updated_state.get("messages_history", []).copy()
            new_chat_history =  updated_state.get("chat_history", []).copy()    
            new_messages_history.extend([
                {"role": "user", "content": state["seeker_request"]},
                {"role": "assistant", "content": follow_up_message}
            ])
            new_chat_history.extend([
                {"role": "user", "content": state["seeker_request"],"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                {"role": "assistant", "content": follow_up_message, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            ])
            return {
                **updated_state,
                "messages_history": new_messages_history,
                "chat_history": new_chat_history,
                "conversation_stage": ConversationStage.PROCEED_TO_FETCH_SLOTS,
                "missing_info": []
            }
        
        # Generate appropriate follow-up question
        follow_up_message = generate_follow_up_question(updated_state, remaining_missing, llm)
        
        # Update conversation history
        new_messages_history = updated_state.get("messages_history", []).copy()
        new_chat_history =  state.get("chat_history", []).copy()
        new_messages_history.extend([
            {"role": "user", "content": state["seeker_request"]},
            {"role": "assistant", "content": follow_up_message}
        ])

        new_chat_history.extend([
            {"role": "user", "content": state["seeker_request"], "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"role": "assistant", "content": follow_up_message, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ])
        
        if remaining_missing[0] == "seeker_contact":
            next_stage = ConversationStage.GATHERING_CONTACT_INFO
        elif remaining_missing[0] == "service_type":
            next_stage = ConversationStage.GATHERING_SERVICE_INFO
        else:
            next_stage = ConversationStage.GATHERING_TIME_PREFERENCES
        return {
            **updated_state,
            "messages_history": new_messages_history,
            "chat_history": new_chat_history,
            "missing_info": remaining_missing,
            "conversation_stage": next_stage
        }


    ##-----------------------------------------     reply on fetched slots   ----------------------------------------

    elif state['conversation_stage'] in [ConversationStage.SLOTS_FETCHED, ConversationStage.CONFIRMING_SLOTS]:
        if state['conversation_stage'] == ConversationStage.SLOTS_FETCHED:
            new_messages_history = state.get("messages_history", []).copy()
            new_chat_history =  state.get("chat_history", []).copy()       
            new_messages_history.extend([
                {"role": "assistant", "content": f"Here are the available slots as per your request : {state['available_slots']}. Please chose one." }
            ])
            new_chat_history.extend([
                {"role": "assistant", "content": f"Here are the available slots as per your request : {state['available_slots']}. Please chose one." , "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            ])

            return {
                **state,
                "messages_history": new_messages_history,
                "chat_history": new_chat_history,
                "conversation_stage": ConversationStage.CONFIRMING_SLOTS
            }
        else:
            ## Make communication with seeker for confirming from the provided slots , 

                    ## add llm prmpt  for loop conversation on confirming the available slot
            try:        
                selected_slot_id = int(state['seeker_request'])
            except:
                selected_slot_id = None

            ##
            if selected_slot_id == None:
                # put followup message for confirming slot
                new_messages_history = state.get("messages_history", []).copy()
                new_chat_history =  state.get("chat_history", []).copy()       
                new_messages_history.extend([
                    {"role": "user", "content": state["seeker_request"]},
                    {"role": "assistant", "content": f"Could not confirm slot from your input , please choose correct slot..." }
                ])
                new_chat_history.extend([
                    {"role": "user", "content": state["seeker_request"],"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                    {"role": "assistant", "content": f"Could not confirm slot from your input , please choose correct slot...", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S") }
                ])

                return {
                    **state,
                    "messages_history": new_messages_history,
                    "chat_history": new_chat_history 
                }

            else:
                ## Proceed to slots_confirmed --> proceed_to_booking
                selected_slot = {}
                for slot in state['available_slots']:
                    if slot['slot_id'] == selected_slot_id:
                        state['selected_slot'] = slot

                new_messages_history = state.get("messages_history", []).copy()
                new_chat_history =  state.get("chat_history", []).copy()       
                new_messages_history.extend([
                    {"role": "user", "content": state["seeker_request"]},
                    {"role": "assistant", "content": f"booking your slot : {state.get('selected_slot','selected_slot_not_found')}." }
                ])
                new_chat_history.extend([
                    {"role": "user", "content": state["seeker_request"],"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                    {"role": "assistant", "content": f"booking your slot : {state.get('selected_slot','selected_slot_not_found')}.", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S") }
                ])

                return {
                    **state,
                    "messages_history": new_messages_history,
                    "chat_history": new_chat_history,
                    "conversation_stage": ConversationStage.PROCEED_TO_BOOKING  ### from here the flow will go to booking/scheduler agent 
                }
    ##---------------------------------------- If No SLOTS FOUND, reply accordingly   ---------------------------------------------------
    elif state['conversation_stage'] == ConversationStage.NO_SLOT_AVAILABLE:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )

        # Prepare context
        preferred_date_time = state.get("time_preferences", {})
        chat_summary = " | ".join([msg["content"] for msg in state.get("chat_history", [])[-3:]])  # last 3 exchanges

        # Direct f-string prompt
        prompt = f"""
        You are a friendly appointment booking assistant.  
        The user requested a slot for following time preference :  {preferred_date_time}.  
        Unfortunately, no slots were available.  

        Recent conversation context: {chat_summary}

        Generate a short, natural reply telling the user no slots are available, 
        and ask them to suggest an alternative timing (different date or time range).
        Keep the tone polite and conversational.
        """

        response = llm.invoke(prompt)
        follow_up_message = response.content.strip()

        new_messages_history = state.get("messages_history", []).copy()
        new_chat_history = state.get("chat_history", []).copy()
        new_messages_history.append({"role": "assistant", "content": follow_up_message})
        new_chat_history.append({
            "role": "assistant",
            "content": follow_up_message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return {
            **state,
            "messages_history": new_messages_history,
            "chat_history": new_chat_history,
            "conversation_stage": ConversationStage.GATHERING_TIME_PREFERENCES  # <-- loop back to asking
        }

    ## For dealing with final booking  stages   
    elif state['conversation_stage'] == ConversationStage.BOOKING_COMPLETE:

        ## give the final message on slot booked by booking/scheduler agent

        new_messages_history = state.get("messages_history", []).copy()
        new_chat_history =  state.get("chat_history", []).copy()       
        new_messages_history.extend([
            {"role": "assistant", "content": f"Successfully booked your slot. Booking confirmation details: {state.get('confirmation','conf_det_not _found')}" }
        ])
        new_chat_history.extend([
            {"role": "assistant", "content": f"Successfully booked your slot. Booking confirmation details: {state.get('confirmation','conf_det_not _found')}" , "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ])

        return {
            **state,
            "messages_history": new_messages_history,
            "chat_history": new_chat_history
        }
    
    elif state['conversation_stage'] == ConversationStage.RESCHEDULING:
        # empty the time preference of the state and go to gathering time preference stage
        state['time_preferences'] = {}
        new_messages_history = state.get("messages_history", []).copy()
        new_chat_history =  state.get("chat_history", []).copy()       
        new_messages_history.extend([
            {"role": "assistant", "content": f"Rescheduling your appointment. Please provide new time preferences." }
        ])
        new_chat_history.extend([
            {"role": "assistant", "content": f"Rescheduling your appointment. Please provide new time preferences.", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ])

        state['old_selected_slot'] = state['selected_slot']  # put the old slot in old_selected_slot for cancelling later
        state['old_appointment'] = state['appointment']  # put the old appointment in old_appointment for cancelling later
        return {
            **state,
            "messages_history": new_messages_history,
            "chat_history": new_chat_history,
            "conversation_stage": ConversationStage.GATHERING_TIME_PREFERENCES,
            "rescheduling_flag": True
        }
    
    elif state['conversation_stage'] == ConversationStage.CANCELLING:
        new_messages_history = state.get("messages_history", []).copy()
        new_chat_history =  state.get("chat_history", []).copy()       
        new_messages_history.extend([
            {"role": "assistant", "content": f"Cancelling your appointment. appointment details: {state.get('appointment','appointment_not_found')}" }
        ])
        new_chat_history.extend([
            {"role": "assistant",
             "content": f"Cancelling your appointment. appointment details: {state.get('appointment','appointment_not_found')}",
             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ])

        state['old_appointment'] = state['appointment']  # put the old appointment in old_appointment for cancelling later
        state['old_selected_slot'] = state['selected_slot']  # put the old slot in old_selected_slot for cancelling later
        state['cancelling_flag'] = True
        return {
            **state,
            "messages_history": new_messages_history,
            "chat_history": new_chat_history
        }
    elif state['conversation_stage'] == ConversationStage.CANCELLEATION_COMPLETE:
        new_messages_history = state.get("messages_history", []).copy()
        new_chat_history =  state.get("chat_history", []).copy()       
        new_messages_history.extend([
            {"role": "assistant", "content": f"Successfully cancelled your appointment. appointment details: {state.get('appointment','appointment_not_found')}" }
        ])
        new_chat_history.extend([
            {"role": "assistant",
             "content": f"Successfully cancelled your appointment. appointment details: {state.get('appointment','appointment_not_found')}",
             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ])

        return {
            **state,
            "messages_history": new_messages_history,
            "chat_history": new_chat_history
        }
    ## other scenario  I dont know !!!!!!  :) 
    else:
        return state

def extract_information_from_message(message: str, llm, stage) -> Dict:
    """Extract structured information from user message using Gemini"""
    
    

    if stage == ConversationStage.GATHERING_SERVICE_INFO:
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting appointment booking information.
            Extract the following from the user message and return as JSON:
            
            {{
            "service_type": "extract service type from user request and our available service otherwise put NA",
            "preferred_date": "YYYY-MM-DD format or null (today is {today})",
            "preferred_time": "morning/afternoon/evening/specific time or null",
            "name": "user's name or null", 
            "contact": "phone or email or null",
            "meeting_preference": "online/in-person/no-preference or null",
            "special_requirements": "any specific requests or null"
            }}
            
            - For extracting service type infer from user request which service he/she is trying to get:
            Here are the complete list of services we provide -
            {service_list}
            If there is no information for service type yet,return null.
            If there is info for service type from user but no available service matching user request, put the value as you infer from users request.
            In Later we will inform user that we do not provide the requested service.

            - Be precise with dates. If user says "tomorrow", calculate the actual date.
            If user says "this weekend", extract as null since it's not specific.
            
            Return ONLY valid JSON, no additional text."""),
            ("user", "{message}")
        ])
        
        chain = extraction_prompt | llm
        service_dao = DAOFactory().get_service_dao()
        try:
            service_list = service_dao.get_all_service_names()
        except Exception as e:
            print(f"Service fetch error: {e}")
            service_list = []
        try:
            response = chain.invoke({
                "message": message,
                "service_list": service_list,
                "today": datetime.now().strftime("%Y-%m-%d")
            })
            
            # Clean the response and parse JSON
            content = response.content.strip()
            if content.startswith("```"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            return json.loads(content)
        except Exception as e:
            print(f"Extraction error: {e}")
            return {}
    else:
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting appointment booking information.
            Extract the following from the user message and return as JSON:
            
            {{
            "service_type": null,
            "preferred_date": "YYYY-MM-DD format or null (today is {today})",
            "preferred_time": "morning/afternoon/evening/specific time or null",
            "name": "user's name or null", 
            "contact": "phone or email or null",
            "meeting_preference": null,
            "special_requirements": null
            }}
            
            - Be precise with dates. If user says "tomorrow", calculate the actual date.
            If user says "this weekend", extract as null since it's not specific.
            
            Return ONLY valid JSON, no additional text."""),
            ("user", "{message}")
        ])

        chain = extraction_prompt | llm
        
        try:
            response = chain.invoke({
                "message": message,
                "today": datetime.now().strftime("%Y-%m-%d")
            })
            
            # Clean the response and parse JSON
            content = response.content.strip()
            if content.startswith("```"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            return json.loads(content)
        except Exception as e:
            print(f"Extraction error: {e}")
            return {}



def identify_missing_information(state: AppointmentState) -> List[str]:
    """Identify what information is still missing"""
    missing = []
    
    # Check required fields
    if not state.get("service_info", {}).get("service_type"):
        missing.append("service_type")
    
    if not state.get("time_preferences", {}).get("preferred_date"):
        missing.append("preferred_date")
        
    if not state.get("seeker_contact", {}).get("name"):
        missing.append("seeker_name")
        
    if not state.get("seeker_contact", {}).get("contact"):
        missing.append("seeker_contact")
    
    return missing

def update_state_with_extracted_info(state: AppointmentState, extracted_info: Dict) -> AppointmentState:
    """Update state with newly extracted information"""
    
    updated_state = state.copy()
    
    # Update service info
    if extracted_info.get("service_type"):
        service_info = updated_state.get("service_info", {})
        service_info["service_type"] = extracted_info["service_type"]
        updated_state["service_info"] = service_info
    
    # Update time preferences
    if extracted_info.get("preferred_date") or extracted_info.get("preferred_time"):
        time_prefs = updated_state.get("time_preferences", {})
        if extracted_info.get("preferred_date"):
            time_prefs["preferred_date"] = extracted_info["preferred_date"]
        if extracted_info.get("preferred_time"):
            time_prefs["preferred_time"] = extracted_info["preferred_time"]
        updated_state["time_preferences"] = time_prefs
    
    # Update contact info
    if extracted_info.get("name") or extracted_info.get("contact"):
        contact_info = updated_state.get("seeker_contact", {})
        if extracted_info.get("name"):
            contact_info["name"] = extracted_info["name"]
        if extracted_info.get("contact"):
            contact_info["contact"] = extracted_info["contact"]
        updated_state["seeker_contact"] = contact_info
    
    return updated_state

def generate_follow_up_question(state: AppointmentState, missing_info: List[str], llm) -> str:
    """Generate contextual follow-up question based on missing information"""
    
    question_map = {
        "service_type": "What type of service are you looking for?",
        "preferred_date": "What date would work best for you?",
        "seeker_name": "Could I get your name for the appointment?",
        "seeker_contact": "How can we reach you to confirm the appointment? (email or phone)"
    }
    
    # Get the most important missing piece
    next_question = question_map.get(missing_info[0], "Could you provide more details?")
    
    # Add context based on what we already know
    context_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a friendly appointment booking assistant. 
        Generate a natural, conversational follow-up question.
        
        Current conversation context:
        - Service type: {service_type}
        - Preferred date: {preferred_date}  
        - User name: {user_name}
        
        Ask for: {missing_item}
        Base question: {base_question}
        
        Make it natural and friendly, referencing what you already know."""),
        ("user", "Generate the follow-up question")
    ])
    
    chain = context_prompt | llm
    
    try:
        response = chain.invoke({
            "service_type": state.get("service_info", {}).get("service_type", "not specified"),
            "preferred_date": state.get("time_preferences", {}).get("preferred_date", "not specified"),
            "user_name": state.get("seeker_contact", {}).get("name", "not specified"),
            "missing_item": missing_info[0],
            "base_question": next_question
        })
        return response.content
    except:
        return next_question







