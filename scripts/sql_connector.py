import os
import urllib
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Get connection config from .env
driver   = os.getenv("DB_DRIVER")
server   = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

# Build the connection string
params = urllib.parse.quote_plus(
    f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
)

# Create SQLAlchemy engine
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", echo=False)

# Insert into Main table
def insert_main(state):
    query = text("""
        INSERT INTO Main (Webtopid, user_message, classify_type, sentiment, category, response)
        VALUES (:webtopid, :usermsg, :classify_type, :sentiment, :category, :response)
    """)
    with engine.begin() as conn:  
        conn.execute(query, {
            "webtopid": state.get("webtopid"),
            "usermsg": state.get("usermsg"),
            "classify_type": state.get("query_type"),
            "sentiment": state.get("sentiment"),
            "category": state.get("category"),
            "response": state.get("response")
        })

# Insert into Status table
def insert_status(state, success=True, failure_reason=None):
    query = text("""
        INSERT INTO Status (Webtopid, user_message, status, failure_reason)
        VALUES (:webtopid, :usermsg, :status, :failure_reason)
    """)
    with engine.begin() as conn:
        conn.execute(query, {
            "webtopid": state.get("webtopid"),
            "usermsg": state.get("usermsg"),
            "status": "Document shared via Power Automate" if success else "Failed",
            "failure_reason": failure_reason if not success else None
        })
