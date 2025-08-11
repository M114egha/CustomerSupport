from typing import Dict, Any
from langgraph.graph import StateGraph
from langgraph.graph import END
from scripts.utils import parse_missing_info
from nodes.classifier import classify_sentiment, classify_category, classify_type
from nodes.handlers import (
    handle_feedback,
    handle_request,
    handle_complaint,
    handle_query,
    handle_missing_info
)
from typing import TypedDict, Optional



class State(TypedDict, total=False):
    usermsg: str
    sentiment: str
    category: str
    query_type: str
    response: str
    applicationId: Optional[str]
    typeOfDoc: Optional[str]
    missing_appid: Optional[bool]
    missing_doc_type: Optional[bool]
    status: Optional[str]
    next_node: Optional[str] 



flow = StateGraph(State)


flow.add_node("classify_sentiment", classify_sentiment)
flow.add_node("classify_category", classify_category)
flow.add_node("classify_type", classify_type)

flow.add_node("handle_feedback", handle_feedback)
flow.add_node("handle_request", handle_request)
flow.add_node("handle_complaint", handle_complaint)
flow.add_node("handle_query", handle_query)
flow.add_node("handle_missing_info", handle_missing_info)



def route_handler(state: State) -> str:
    qtype = state.get("query_type", "").lower()
    if qtype == "feedback":
        return "handle_feedback"
    elif qtype == "request":
        return "handle_request"
    elif qtype == "complaint":
        return "handle_complaint"
    else:
        return "handle_query"

def route_by_next_node(state: State) -> str:
    return state["next_node"] if "next_node" in state else END


flow.set_entry_point("classify_sentiment")
flow.add_edge("classify_sentiment", "classify_category")
flow.add_edge("classify_category", "classify_type")
flow.add_conditional_edges("classify_type", route_handler)


flow.add_edge("handle_feedback", "__end__")
flow.add_edge("handle_complaint", "__end__")
flow.add_edge("handle_query", "__end__")

flow.add_conditional_edges("handle_request", route_by_next_node)
flow.add_conditional_edges("handle_missing_info", route_by_next_node)




workflow = flow.compile()


def run_workflow(state: dict) -> dict:
    return workflow.invoke(state)


workflow.get_graph().draw_mermaid()
