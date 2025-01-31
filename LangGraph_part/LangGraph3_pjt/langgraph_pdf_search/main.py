# main.py

import os
from dotenv import load_dotenv
from graph_state import GraphState
from nodes import retrieve_document, llm_answer, relevance_check, rewrite, search_on_web
from edges import is_relevant
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from easy_langsmith import logging
from langchain_core.runnables import RunnableConfig
from rag.pdf import PDFRetrievalChain

load_dotenv()

# LangSmith 추적 설정
logging.langsmith("CH1-LANGGRAPH")

def create_workflow(pdf_path):
    # PDF 체인 생성
    pdf = PDFRetrievalChain([pdf_path]).create_chain()
    pdf_retriever = pdf.retriever
    pdf_chain = pdf.chain

    # 그래프 생성
    workflow = StateGraph(GraphState)

    # 노드 추가
    workflow.add_node("retrieve", lambda state: retrieve_document(state, pdf_retriever))
    workflow.add_node("llm_answer", lambda state: llm_answer(state, pdf_chain))
    workflow.add_node("relevance_check", relevance_check)
    workflow.add_node("rewrite", rewrite)
    workflow.add_node("search_on_web", search_on_web)

    # 엣지 추가
    workflow.add_edge("retrieve", "llm_answer")
    workflow.add_edge("llm_answer", "relevance_check")
    workflow.add_edge("rewrite", "search_on_web")
    workflow.add_edge("search_on_web", "llm_answer")

    # 조건부 엣지 추가
    workflow.add_conditional_edges(
        "relevance_check",
        is_relevant,
        {
            "grounded": END,
            "notGrounded": "rewrite",
            "notSure": "rewrite",
        },
    )

    workflow.set_entry_point("retrieve")

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

def process_question(app, question):
    inputs = GraphState(question=question)
    config = RunnableConfig(
        configurable={
            "thread_id": "CORRECTIVE-SEARCH-RAG"
        }
    )
    result = app.invoke(inputs, config=config)
    return result.get('answer', '답변을 생성하지 못했습니다.')

if __name__ == "__main__":
    pdf_path = input("PDF 파일 경로를 입력하세요: ")
    app = create_workflow(pdf_path)
    
    print("질문을 입력하세요. 종료하려면 'quit'를 입력하세요.")
    while True:
        question = input("질문: ")
        if question.lower() == 'quit':
            print("프로그램을 종료합니다.")
            break
        
        answer = process_question(app, question)
        print("\n답변:")
        print(answer)
        print("\n")