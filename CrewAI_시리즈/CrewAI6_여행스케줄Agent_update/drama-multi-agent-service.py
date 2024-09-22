import streamlit as st
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

# 마크다운 텍스트 처리 함수
def process_markdown(text):
    return text.replace('\n', '\n\n')

# 검색 도구 초기화
search_tool = DuckDuckGoSearchRun()

# Streamlit 페이지 설정
st.set_page_config(page_title="AI 드라마 분석 도우미", page_icon="🎬", layout="wide")

# 검색 결과 캐싱 및 필터링을 위한 클래스
class SearchCache:
    def __init__(self):
        self.cache: Dict[str, List[str]] = {}
        self.search_count: Dict[str, int] = {}

    def get(self, query: str) -> List[str]:
        return self.cache.get(query, [])

    def add(self, query: str, results: List[str]):
        self.cache[query] = results
        self.search_count[query] = self.search_count.get(query, 0) + 1

    def get_search_count(self, query: str) -> int:
        return self.search_count.get(query, 0)

search_cache = SearchCache()

# CSS를 사용하여 폰트 크기와 스타일 조정
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .medium-font {
        font-size:20px !important;
    }
    .small-font {
        font-size:14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 타이틀 표시
st.markdown('<p class="big-font">AI 드라마 분석 도우미</p>', unsafe_allow_html=True)

# OpenAI와 Anthropic 모델 초기화
gpt = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7,max_tokens=4000)
claude = ChatAnthropic(model="claude-3-5-sonnet-20240620", anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"), temperature=0.7,max_tokens=4000)

# 에이전트 정의
content_reporter = Agent(
    role='컨텐츠 기자',
    goal='드라마의 각 에피소드 내용을 정확하게 요약하고 보고',
    backstory='10년 경력의 드라마 전문 기자로, 정확하고 간결한 에피소드 요약을 제공합니다.',
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    llm=gpt
)

drama_writer = Agent(
    role='드라마 작가',
    goal='미방영 에피소드의 흥미진진한 내용 창작',
    backstory='베테랑 드라마 작가로, 시청자들을 사로잡는 흥미진진한 스토리를 만들어냅니다.',
    verbose=True,
    allow_delegation=False,
    llm=claude
)

drama_critic = Agent(
    role='드라마 비평가',
    goal='작가가 제시한 다음 화 내용에 대한 객관적이고 냉정한 평가',
    backstory='20년 경력의 드라마 비평가로, 작품을 다각도로 분석하고 객관적인 평가를 제공합니다.',
    verbose=True,
    allow_delegation=False,
    llm=gpt
)

# 사이드바에 입력 섹션 생성
with st.sidebar:
    st.header("드라마 정보 입력")
    drama_title = st.text_input("드라마 제목", value="엄마친구아들")
    current_episode = st.number_input("현재 방영된 회차", min_value=1, value=1)
    next_episode = current_episode + 1

# 메인 화면에 결과 표시 섹션
if st.sidebar.button("드라마 분석 시작"):
    # 태스크 1: 드라마 내용 요약
    task1 = Task(
        description=f"{drama_title}의 1화부터 {current_episode}화까지의 내용을 검색하고 각 에피소드별로 간단히 요약해주세요.",
        agent=content_reporter
    )

    # 태스크 2: 다음 화 내용 창작
    task2 = Task(
        description=f"{drama_title}의 {next_episode}화 내용을 창의적이고 흥미진진하게 만들어주세요. 이전 에피소드의 내용을 고려하여 연속성 있는 스토리를 제시해주세요.",
        agent=drama_writer
    )

    # 태스크 3: 다음 화 내용 평가
    task3 = Task(
        description=f"드라마 작가가 제시한 {drama_title}의 {next_episode}화 내용을 객관적이고 냉정하게 평가해주세요. 스토리의 개연성, 캐릭터 발전, 긴장감 등 다양한 측면에서 분석해주세요.",
        agent=drama_critic
    )

    # Crew 생성 및 실행
    crew = Crew(
        agents=[content_reporter, drama_writer, drama_critic],
        tasks=[task1, task2, task3],
        verbose=2
    )

    st.markdown('<p class="medium-font">드라마 분석 결과</p>', unsafe_allow_html=True)

    with st.spinner('드라마를 분석하고 있습니다...'):
        result = crew.kickoff()

        # 결과 표시
        st.subheader("에피소드 요약")
        st.markdown(process_markdown(result[0]), unsafe_allow_html=True)

        st.subheader(f"{next_episode}화 예상 내용")
        st.markdown(process_markdown(result[1]), unsafe_allow_html=True)

        st.subheader("다음 화 내용 평가")
        st.markdown(process_markdown(result[2]), unsafe_allow_html=True)

# 저장 기능
if st.button("분석 결과 저장"):
    with open(f"{drama_title}_analysis.txt", "w", encoding="utf-8") as f:
        f.write(f"드라마 제목: {drama_title}\n")
        f.write(f"현재 방영 회차: {current_episode}\n\n")
        f.write("에피소드 요약:\n")
        f.write(result[0] + "\n\n")
        f.write(f"{next_episode}화 예상 내용:\n")
        f.write(result[1] + "\n\n")
        f.write("다음 화 내용 평가:\n")
        f.write(result[2])
    
    st.success(f"분석 결과가 '{drama_title}_analysis.txt' 파일로 저장되었습니다.")

# 저장된 파일 다운로드 버튼
if os.path.exists(f"{drama_title}_analysis.txt"):
    with open(f"{drama_title}_analysis.txt", "r", encoding="utf-8") as file:
        st.download_button(
            label="분석 결과 다운로드",
            data=file.read(),
            file_name=f"{drama_title}_analysis.txt",
            mime="text/plain"
        )
