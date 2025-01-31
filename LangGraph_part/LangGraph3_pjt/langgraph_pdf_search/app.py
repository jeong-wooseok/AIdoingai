import streamlit as st
import os
import base64
import time
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

@st.cache_resource
def create_workflow(pdf_paths):
    # 경로 정규화
    normalized_paths = [os.path.normpath(os.path.abspath(path)) for path in pdf_paths]
    
    # PDF 체인 생성
    pdf = PDFRetrievalChain(normalized_paths).create_chain()
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
    return result

# Streamlit 앱
st.title("PDF 기반 Q&A 챗봇")

# 현재 스크립트의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# data 폴더 내의 모든 PDF 파일 경로 가져오기
data_folder = os.path.join(current_dir, "data")
pdf_files = [os.path.join(data_folder, f) for f in os.listdir(data_folder) if f.endswith('.pdf')]

if pdf_files:
    st.success(f"{len(pdf_files)}개의 PDF 파일을 찾았습니다.")
    
    # 각 PDF 파일의 내용 표시
    for pdf_path in pdf_files:
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_content = pdf_file.read()
            
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            st.markdown(f"### {os.path.basename(pdf_path)}")
            st.markdown(f'<embed src="data:application/pdf;base64,{pdf_base64}" width="700" height="400" type="application/pdf">', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"{pdf_path} 파일 처리 중 오류 발생: {str(e)}")

    try:
        # 워크플로우 생성
        app = create_workflow(pdf_files)

        # 채팅 인터페이스
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("질문을 입력하세요."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                start_time = time.time()
                response = process_question(app, prompt)
                end_time = time.time()

                st.markdown(f"**답변:** {response.get('answer', '답변을 생성하지 못했습니다.')}")
                st.markdown("---")
                st.markdown("**상세 정보:**")
                st.markdown(f"- 검색된 문서: {response.get('context', '없음')}")
                st.markdown(f"- 관련성 점수: {response.get('relevance', '없음')}")
                st.markdown(f"- 처리 시간: {end_time - start_time:.2f}초")

            st.session_state.messages.append({"role": "assistant", "content": response.get('answer', '답변을 생성하지 못했습니다.')})

    except Exception as e:
        st.error(f"워크플로우 생성 중 오류가 발생했습니다: {str(e)}")

else:
    st.error("data 폴더에 PDF 파일이 없습니다.")

# 디버그 정보 표시
st.sidebar.title("디버그 정보")
for pdf_path in pdf_files:
    st.sidebar.write(f"PDF 파일: {os.path.basename(pdf_path)}")
    st.sidebar.write(f"절대 경로: {os.path.abspath(pdf_path)}")
    st.sidebar.write(f"파일 크기: {os.path.getsize(pdf_path)} bytes")
st.sidebar.write(f"총 PDF 파일 수: {len(pdf_files)}")