import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import pathlib

# 프로젝트 루트 디렉토리 찾기
root_dir = pathlib.Path(__file__).parent.parent
env_path = root_dir / '.env'

# .env 파일 로드
load_dotenv(dotenv_path=env_path)

st.set_page_config(
    page_title="YouTube 영상 요약 봇",
    page_icon="🎥",
    layout="wide"
)

st.title("YouTube 영상 요약 봇 🎥")
st.markdown("""
이 앱은 YouTube 영상의 내용을 자동으로 요약해주는 서비스입니다.
영상 URL을 입력하시면 핵심 내용을 추출하여 보여드립니다.
""")

# 사이드바에 모델 선택 추가
with st.sidebar:
    st.header("설정")
    model_type = st.selectbox(
        "AI 모델 선택",
        options=["OpenAI GPT-4", "Google Gemini"],
        format_func=lambda x: {
            "OpenAI GPT-4": "OpenAI GPT-4o-mini",
            "Google Gemini": "Google Gemini 1.5 Pro"
        }[x],
        index=0
    )

    # API 키 표시 (읽기 전용)
    if model_type == "OpenAI GPT-4":
        api_key = os.getenv("OPENAI_API_KEY")
        st.info("OpenAI API 키가 설정되어 있습니다." if api_key else "OpenAI API 키가 설정되어 있지 않습니다. .env 파일을 확인해주세요.")
    else:
        api_key = os.getenv("GOOGLE_API_KEY")
        st.info("Google API 키가 설정되어 있습니다." if api_key else "Google API 키가 설정되어 있지 않습니다. .env 파일을 확인해주세요.")

# 메인 입력 폼
with st.form("youtube_url_form"):
    url = st.text_input("YouTube URL 입력", placeholder="https://www.youtube.com/watch?v=...")
    submit_button = st.form_submit_button("영상 요약하기")

    if submit_button:
        if not url:
            st.error("YouTube URL을 입력해주세요.")
        else:
            try:
                with st.spinner("영상을 분석하고 있습니다... 잠시만 기다려주세요."):
                    # FastAPI 서버로 요청 보내기
                    response = requests.post(
                        "http://localhost:8000/summarize",
                        json={
                            "url": url,
                            "model_type": model_type
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # 결과 표시
                        st.success("요약이 완료되었습니다!")
                        
                        # 제목
                        st.header(result["title"])
                        
                        # 요약
                        st.subheader("📝 요약")
                        st.write(result["summary"])
                        
                        # 키포인트
                        st.subheader("🔑 주요 포인트")
                        for point in result["key_points"]:
                            st.markdown(f"- {point}")
                    else:
                        st.error(f"오류가 발생했습니다: {response.json()['detail']}")
            except Exception as e:
                st.error(f"서비스 연결 중 오류가 발생했습니다: {str(e)}")

# 푸터
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit") 