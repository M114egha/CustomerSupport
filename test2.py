from langgraph.graph import StateGraph, END

class State(dict): pass

def say_hello(state): 
    print("Hello")
    return state

graph = StateGraph(State)
graph.add_node("start", say_hello)
graph.set_entry_point("start")
graph.add_edge("start", END)

workflow = graph.compile()

print(workflow.get_graph().draw_mermaid())
