import streamlit as st
from main import handle_request, handle_missing_info

# Define handlers
handlers = {
    "handle_request": handle_request,
    "handle_missing_info": handle_missing_info
}

st.set_page_config(page_title="Support Assistant", layout="centered")

# Initialize session state
if "state" not in st.session_state:
    st.session_state.state = {
        "usermsg": "",
        "next_node": "handle_request"
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 Support Assistant")

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message here..."):
    # New user input
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Set usermsg to this input and store it
    st.session_state.state["usermsg"] = prompt

    # Reset flags if needed
    st.session_state.state["next_node"] = st.session_state.state.get("next_node", "handle_request")

    while True:
        current_node = st.session_state.state.get("next_node")

        if current_node is None or current_node.lower() == "end":
            st.session_state.messages.append({
                "role": "assistant",
                "content": "✅ Conversation ended."
            })
            break

        handler_fn = handlers.get(current_node)
        if not handler_fn:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Unknown handler: {current_node}"
            })
            break

        # ✅ Important: do NOT reassign usermsg inside loop
        st.session_state.state = handler_fn(st.session_state.state)

        # Get bot response
        bot_msg = st.session_state.state.get("response", "🤖 No response.")
        st.session_state.messages.append({"role": "assistant", "content": bot_msg})

        # Exit if awaiting more info or end of flow
        if st.session_state.state.get("status") == "awaiting_info":
            break

        if st.session_state.state.get("next_node") in [None, "END"]:
            break
