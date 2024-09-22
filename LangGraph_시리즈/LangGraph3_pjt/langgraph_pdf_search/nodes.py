# nodes.py

from graph_state import GraphState
from rag.utils import format_docs, format_searched_docs
from langchain_upstage import UpstageGroundednessCheck
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
import os

upstage_ground_checker = UpstageGroundednessCheck(api_key=os.getenv("UPSTAGE_API_KEY", "default_value"))

def retrieve_document(state: GraphState, pdf_retriever) -> GraphState:
    retrieved_docs = pdf_retriever.invoke(state["question"])
    retrieved_docs = format_docs(retrieved_docs)
    return GraphState(context=retrieved_docs)

def llm_answer(state: GraphState, pdf_chain) -> GraphState:
    question = state["question"]
    context = state["context"]
    response = pdf_chain.invoke({"question": question, "context": context})
    return GraphState(answer=response)

def rewrite(state):
    question = state["question"]
    answer = state["answer"]
    context = state["context"]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a professional prompt rewriter. Your task is to generate the question in order to get additional information that is now shown in the context."
                "Your generated question will be searched on the web to find relevant information.",
            ),
            (
                "human",
                "Rewrite the question to get additional information to get the answer."
                "\n\nHere is the initial question:\n ------- \n{question}\n ------- \n"
                "\n\nHere is the initial context:\n ------- \n{context}\n ------- \n"
                "\n\nHere is the initial answer to the question:\n ------- \n{answer}\n ------- \n"
                "\n\nFormulate an improved question in Korean:",
            ),
        ]
    )
    model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    chain = prompt | model | StrOutputParser()
    response = chain.invoke(
        {"question": question, "answer": answer, "context": context}
    )
    return GraphState(question=response)

def search_on_web(state: GraphState) -> GraphState:
    search_tool = TavilySearchResults(max_results=5)
    search_result = search_tool.invoke({"query": state["question"]})
    search_result = format_searched_docs(search_result)
    return GraphState(
        context=search_result,
    )

def relevance_check(state: GraphState) -> GraphState:
    print("relevance_check", state)
    response = upstage_ground_checker.run(
        {"context": state["context"], "answer": state["answer"]}
    )
    return GraphState(
        relevance=response, question=state["question"], answer=state["answer"]
    )