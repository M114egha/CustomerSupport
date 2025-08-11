# handlers.py
from typing import Dict, Any
from langgraph.graph import StateGraph, END
import re
import os
import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from scripts.rag import retriever   
from scripts.utils import extract_application_id
from scripts.utils import extract_type_of_doc


llm = ChatGroq(model_name="llama3-70b-8192", temperature=0)


POWER_AUTOMATE_URL = os.getenv("POWER_AUTOMATE_URL")   # put this in .env


def handle_feedback(state: Dict[str, Any]) -> Dict[str, Any]:
    state["response"] = "Thank you for your feedback. We appreciate your input."
    state["source"] = "CANNED"
    return state




'''
def handle_request(state: Dict[str, Any]) -> Dict[str, Any]:
    webtopid = state.get("webtopid")
    if not webtopid:
        state["response"] = "Request received but no webtopid was supplied."
        state["source"] = "ERROR"
        return state

    payload = {"webtopid": webtopid}
    try:
        r = requests.post(POWER_AUTOMATE_URL, json=payload, timeout=15)
        if r.status_code == 200:
            state["response"] = (
                "Your document is being retrieved. You will receive it shortly."
            )
            state["source"] = "POWER_AUTOMATE"
        else:
            state["response"] = (
                f"Document retrieval failed (status {r.status_code})."
            )
            state["source"] = "ERROR"
    except Exception as exc:
        state["response"] = f"Unable to trigger document retrieval: {exc}"
        state["source"] = "ERROR"
    return state
'''

def handle_request(state: Dict[str, Any]) -> Dict[str, Any]:
    usermsg = state.get("usermsg", "")

    if not state.get("applicationId"):
        app_id = extract_application_id(usermsg)
        if app_id:
            state["applicationId"] = app_id
            state["missing_appid"] = False
    elif state.get("applicationId"):
        state["missing_appid"] = False

    if not state.get("typeOfDoc"):
        doc_type = extract_type_of_doc(usermsg)
        if doc_type:
            state["typeOfDoc"] = doc_type
            state["missing_doc_type"] = False
    elif state.get("typeOfDoc"):
        state["missing_doc_type"] = False 

   
    if not state.get("applicationId"):
        state["status"] = "awaiting_info"
        state["response"] = "ℹ️ Please provide your Application ID."
        state["missing_appid"] = True
        state["next_node"] = "handle_missing_info"

    elif not state.get("typeOfDoc"):
        state["status"] = "awaiting_info"
        state["response"] = "ℹ️ Please specify the document you are requesting (e.g., Sanction Letter, Application Document)."
        state["missing_doc_type"] = True
        state["next_node"] = "handle_missing_info"

    else:
        state["status"] = "ready"
        state["response"] = f"✅ Thank you. Your request for {state['typeOfDoc']} for application ID {state['applicationId']} is being processed."
        state["next_node"] = None

    return state




def handle_missing_info(state: Dict[str, Any]) -> Dict[str, Any]:
    user_msg = state.get("usermsg", "")

    # Try to extract missing fields from current message
    if not state.get("applicationId"):
        extracted_id = extract_application_id(user_msg)
        if extracted_id:
            state["applicationId"] = extracted_id
            state["missing_appid"] = False

    if not state.get("typeOfDoc"):
        extracted_doc = extract_type_of_doc(user_msg)
        if extracted_doc:
            state["typeOfDoc"] = extracted_doc
            state["missing_doc_type"] = False

  
    if state.get("applicationId") and state.get("typeOfDoc"):
        state["status"] = "info_completed"
        state["response"] = "✅ Got the missing info. Proceeding to process your request..."
        state["next_node"] = "handle_request"

    else:
        # Still missing something
        missing = []
        if not state.get("applicationId"):
            missing.append("application ID")
            state["missing_appid"] = True
        if not state.get("typeOfDoc"):
            missing.append("document type")
            state["missing_doc_type"] = True

        state["status"] = "awaiting_info"
        state["response"] = f"Still missing: {', '.join(missing)}"
        state["next_node"] = "handle_missing_info"

    return state

def handle_complaint(state: Dict[str, Any]) -> Dict[str, Any]:
    prompt = ChatPromptTemplate.from_template(
        "Politely acknowledge the complaint, apologise once, and reassure the customer in no more than two sentences:\nComplaint: {text}"
    )
    result = (prompt | llm).invoke({"text": state["usermsg"]})
    state["response"] = result.content.strip()
    state["source"] = "LLM"
    return state


def handle_query(state):
    prompt = ChatPromptTemplate.from_template("""
You are a financial services assistant. Based only on the context below, generate a precise, professional response to the customer's query. 

Strict rules:
- Do NOT invent or add any information not present in the context.
- Do NOT include generic phrases, disclaimers, or toll-free numbers.
- Do NOT try to be conversational.
- Answer the query concisely, factually, and to the point.
- If no answer is found, say: "We are unable to find the requested information at this time."

Context:
{context}

Query:
{query}

Strict Response:
""")

    query = state.get("usermsg", "")
    relevant_docs = relevant_docs = retriever.invoke(query)
    if not relevant_docs:
        state["response"] = "We are unable to find the requested information at this time."
        state["source"] = "RAG"
        return state

    context = relevant_docs[0].page_content.strip()
    result = (prompt | llm).invoke({"context": context, "query": query})

    state["response"] = result.content.strip()
    state["source"] = "RAG"
    return state
