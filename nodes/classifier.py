from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model_name="llama3-70b-8192", temperature=0)

def classify_sentiment(state):
    prompt = ChatPromptTemplate.from_template(
        "What is the sentiment of this customer query? Respond only with one word: Positive, Neutral, or Negative.\nQuery: {text}"
    )
    result = (prompt | llm).invoke({"text": state["usermsg"]})
    state["sentiment"] = result.content.strip()
    return state

def classify_category(state):
    prompt = ChatPromptTemplate.from_template(
        "Categorize this customer query with only one word: Technical, Billing, General, or Feedback.\nQuery: {text}"
    )
    result = (prompt | llm).invoke({"text": state["usermsg"]})
    state["category"] = result.content.strip()
    return state

def classify_type(state):
    prompt = ChatPromptTemplate.from_template(
        "Classify the query type using only one word: Query, Request, or Complaint.\nQuery: {text}"
    )
    result = (prompt | llm).invoke({"text": state["usermsg"]})
    state["query_type"] = result.content.strip()
    return state
