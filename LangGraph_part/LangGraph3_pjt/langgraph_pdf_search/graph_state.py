from typing import TypedDict

class GraphState(TypedDict):
    question: str
    context: str
    answer: str
    relevance: str