from graph_state import GraphState

def is_relevant(state: GraphState) -> str:
    relevance = state["relevance"]
    if relevance == "grounded":
        return "grounded"
    elif relevance == "notGrounded":
        return "notGrounded"
    else:
        return "notSure"