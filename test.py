from main import handle_request, handle_missing_info

# Define your handlers manually in a lookup
handlers = {
    "handle_request": handle_request,
    "handle_missing_info": handle_missing_info
}

# Initial state
state = {
    "usermsg": input("You: "),
    "next_node": "handle_request"   
}

while True:
    current_node = state.get("next_node")

    # Safety exit
    if current_node is None or current_node == "END":
        print("\n✅ Conversation ended.")
        break

    # Call the correct handler
    handler_fn = handlers.get(current_node)
    if not handler_fn:
        print(f"\n❌ Unknown handler: {current_node}")
        break

    # Process state
    state = handler_fn(state)

    print(f"\n🤖 Bot: {state.get('response')}")

    # Get user input if bot is expecting it
    if state.get("status") == "awaiting_info":
        state["usermsg"] = input("\nYou: ")
