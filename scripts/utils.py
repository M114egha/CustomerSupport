import re
from typing import Optional
from typing import Dict, Any

def extract_application_id(user_msg: str) -> Optional[str]:
    """
    Extracts application ID that matches the format: 3 digits + 2 uppercase letters + 7 digits.
    Example match: 074PZ8600310
    """
    match = re.search(r"\b\d{3}[A-Z]{2}\d{7}\b", user_msg.upper())
    return match.group(0) if match else None


def extract_type_of_doc(user_msg: str) -> str | None:
    """
    Extracts document type based on known types or fuzzy matches.
    """
    doc_types = {
        "sanction": "Sanction Letter",
        "welcome": "Welcome Letter",
        "statement": "Loan Statement",
        "repayment": "Repayment Schedule",
        "foreclosure": "Foreclosure Letter",
        "interest": "Interest Certificate",
        "no dues": "No Dues Certificate",
        "application": "Loan Application Document",
    }

    msg_lower = user_msg.lower()
    for keyword, proper_name in doc_types.items():
        if keyword in msg_lower:
            return proper_name

    return None
