import streamlit as st
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
from langchain.tools import BaseTool
from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi
import re

load_dotenv()

# 마크다운 텍스트 처리 함수
def process_markdown(text):
    return text.replace('\n', '\n\n')

# YouTube 검색 및 자막 가져오기 도구
class YouTubeSearchTool(BaseTool):
    name = "youtube_search"
    description = "Searches YouTube for videos and retrieves their transcripts. Input should be a search query string."

    def get_video_id(self, url):
        video_id = re.search(r"v=([^&]+)", url)
        if video_id:
            return video_id.group(1)
        return None

    def get_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
            return " ".join([entry['text'] for entry in transcript])
        except Exception as e:
            print(f"자막을 가져오는 데 실패했습니다: {str(e)}")
            return "자막을 가져오는 데 실패했습니다."

    def _run(self, query: str) -> str:
        videos_search = VideosSearch(query, limit=3)
        results = videos_search.result()
        
        output = []
        for video in results['result']:
            title = video['title']
            link = video['link']
            video_id = self.get_video_id(link)
            if video_id:
                transcript = self.get_transcript(video_id)
            else:
                transcript = "자막을 가져올 수 없습니다."
            
            output.append(f"제목: {title}\n링크: {link}\n자막: {transcript}\n")
        
        return "\n".join(output)

    def _arun(self, query: str):
        raise NotImplementedError("YouTubeSearchTool does not support async")

# YouTube 검색 도구 초기화
youtube_search_tool = YouTubeSearchTool()

# Streamlit 페이지 설정
st.set_page_config(page_title="AI 드라마 분석 도우미", page_icon="🎬", layout="wide")

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
gpt = ChatOpenAI(model="gpt-4o-mini",
             api_key=os.getenv("OPENAI_API_KEY"), 
             temperature=0.7,
             max_tokens=4000)

try:
    claude = ChatAnthropic(model="claude-3-5-sonnet-20240620",
                         anthropic_api_key=os.getenv("Anthropic_API_KEY"),
                         temperature=0.7,
                         max_tokens=4000)
except Exception as e:
    st.warning("Claude API를 초기화하는 데 실패했습니다. GPT-4를 대체 모델로 사용합니다.")
    claude = gpt  # Claude 초기화 실패 시 GPT-4를 사용

# 에이전트 정의
content_reporter = Agent(
    role='컨텐츠 기자',
    goal='드라마의 각 에피소드 내용을 정리, 주요한 포인트와 드라마의 분위기를 잘 드러냅니다',
    backstory='팩트 위주로 꼼꼼하게 정리하는 성격을 가지고 있습니다. 전반적인 스토리가 이해가되는데 큰 도움을 줍니다.',
    verbose=True,
    allow_delegation=False,
    tools=[youtube_search_tool],
    llm=gpt
)

drama_writer = Agent(
    role='드라마 작가',
    goal='미방영 에피소드의 흥미진진한 내용 창작',
    backstory='베테랑 드라마 작가로, 시청자들을 사로잡는 흥미진진한 스토리를 만들어냅니다. 정황 및 지난화와의 스토리 개연성을 중요하게 고려합니다.',
    verbose=True,
    allow_delegation=False,
    llm=gpt
)

youtube_creator = Agent(
    role='유튜브 크리에이터',
    goal='드라마 내용을 바탕으로 흥미로운 유튜브 컨텐츠 기획',
    backstory='드라마 작가가 만든 이야기를 재밌게 풀어냅니다. 드라마 팬들의 관심을 끄는 로지컬한 스토리라인을 구성하고, 재미있게 스토리텔링을 하며 상상력을 자극합니다.',
    verbose=True,
    allow_delegation=False,
    llm=gpt
)

# Streamlit 세션 상태 초기화
if 'drama_title' not in st.session_state:
    st.session_state.drama_title = "엄마 친구 아들"
if 'current_episode' not in st.session_state:
    st.session_state.current_episode = 1
if 'result' not in st.session_state:
    st.session_state.result = [""] * 4

# 사이드바에 입력 섹션 생성
with st.sidebar:
    st.header("드라마 정보 입력")
    st.session_state.drama_title = st.text_input("드라마 제목", value=st.session_state.drama_title)
    st.session_state.current_episode = st.number_input("현재 방영된 회차", min_value=1, value=st.session_state.current_episode)
    next_episode = st.session_state.current_episode + 1

# 메인 화면에 결과 표시 섹션
if st.sidebar.button("드라마 분석 시작"):
    # 태스크 1: 드라마 내용 요약
    task1 = Task(
        description=f"{st.session_state.drama_title}의 1화부터 {st.session_state.current_episode}화까지의 내용을 YouTube에서 검색하고 자막을 가져와서 각 에피소드별로 정리해주세요. 전체 자막을 분석하고 중요한 내용을 정리해주세요.",
        agent=content_reporter,
        expected_output="각 에피소드의 주요 사건과 인물들의 발전을 포함한 정리"
    )

    # 태스크 2: 다음 화 내용 창작
    task2 = Task(
        description=f"{st.session_state.drama_title}의 {next_episode}화 내용을 창의적이고 흥미진진하게 만들어주세요. 이전 에피소드의 내용을 고려하여 연속성 있는 스토리를 제시해주세요.",
        agent=drama_writer,
        expected_output="다음 화의 예상 스토리라인, 주요 사건, 그리고 캐릭터 발전 계획"
    )

    # 태스크 3: 유튜브 컨텐츠 기획
    task3 = Task(
        description=f" {st.session_state.drama_title}의 {st.session_state.current_episode}와 {next_episode}화 예상 내용을 바탕으로 흥미로운 20분 내외의 유튜브 영상 스크립트를 작성해주세요. 드라마 팬들의 관심을 끌 수 있는 내용으로 구성해주세요.",
        agent=youtube_creator,
        expected_output="다음 화의 예상 내용을 바탕으로 한 유튜브 영상 스크립트, 주요 예측 포인트, 팬들의 관심을 끌 수 있는 요소"
    )

    # Crew 생성 및 실행
    crew = Crew(
        agents=[content_reporter, drama_writer, youtube_creator],
        tasks=[task1, task2, task3],
        verbose=2
    )

    st.markdown('<p class="medium-font">드라마 분석 결과</p>', unsafe_allow_html=True)

    with st.spinner('드라마를 분석하고 있습니다...'):
        try:
            results = crew.kickoff()
            st.write("AI 응답 결과:", results)  # 디버깅을 위한 출력
            
            # 결과를 session_state에 저장
            for i, result in enumerate(results):
                if i < len(st.session_state.result):
                    st.session_state.result[i] = result
            
            # 결과 표시
            st.subheader("에피소드 요약")
            st.markdown(process_markdown(st.session_state.result[0]), unsafe_allow_html=True)

            st.subheader(f"{next_episode}화 예상 내용")
            st.markdown(process_markdown(st.session_state.result[1]), unsafe_allow_html=True)

            st.subheader("유튜브 컨텐츠 기획")
            st.markdown(process_markdown(st.session_state.result[2]), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
            st.write(f"오류 상세: {e}")

# 사용자 피드백 입력 받기
user_feedback = st.text_area("유튜브 컨텐츠에 대한 피드백을 입력해주세요:", "")

if st.button("피드백 반영하여 스크립트 수정"):
    with st.spinner('피드백을 반영하여 스크립트를 수정 중입니다...'):
        # 태스크 4: 피드백 기반 스크립트 수정
        task4 = Task(
            description=f"사용자의 피드백을 반영하여 유튜브 스크립트를 수정해주세요. 원본 스크립트: {st.session_state.result[2]}, 사용자 피드백: {user_feedback}",
            agent=youtube_creator,
            expected_output="사용자 피드백이 반영된 개선된 유튜브 스크립트"
        )
        
        feedback_crew = Crew(
            agents=[youtube_creator],
            tasks=[task4],
            verbose=2
        )
        
        try:
            feedback_result = feedback_crew.kickoff()
            st.write("피드백 반영 결과:", feedback_result)  # 디버깅을 위한 출력
            if feedback_result and len(feedback_result) > 0:
                st.session_state.result[3] = feedback_result[0]  # 수정된 스크립트를 result에 추가
            
            st.subheader("피드백 반영 후 수정된 유튜브 스크립트")
            st.markdown(process_markdown(st.session_state.result[3]), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"스크립트 수정 중 오류가 발생했습니다: {str(e)}")
            st.write(f"오류 상세: {e}")

# 저장 기능
if st.button("분석 결과 저장"):
    if any(st.session_state.result):  # result에 내용이 있는 경우에만 저장
        with open(f"{st.session_state.drama_title}_analysis.txt", "w", encoding="utf-8") as f:
            f.write(f"드라마 제목: {st.session_state.drama_title}\n")
            f.write(f"현재 방영 회차: {st.session_state.current_episode}\n\n")
            f.write("에피소드 요약:\n")
            f.write(st.session_state.result[0] + "\n\n")
            f.write(f"{next_episode}화 예상 내용:\n")
            f.write(st.session_state.result[1] + "\n\n")
            f.write("유튜브 컨텐츠 기획:\n")
            f.write(st.session_state.result[2] + "\n\n")
            if len(st.session_state.result) > 3 and st.session_state.result[3]:
                f.write("피드백 반영 후 수정된 유튜브 스크립트:\n")
                f.write(st.session_state.result[3])
        
        st.success(f"분석 결과가 '{st.session_state.drama_title}_analysis.txt' 파일로 저장되었습니다.")
    else:
        st.warning("저장할 분석 결과가 없습니다. 먼저 드라마 분석을 실행해주세요.")

# 저장된 파일 다운로드 버튼
if os.path.exists(f"{st.session_state.drama_title}_analysis.txt"):
    with open(f"{st.session_state.drama_title}_analysis.txt", "r", encoding="utf-8") as file:
        st.download_button(
            label="분석 결과 다운로드",
            data=file.read(),
            file_name=f"{st.session_state.drama_title}_analysis.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    st.write("AI 드라마 분석 도우미가 실행되었습니다.")
    st.write("사이드바에서 드라마 정보를 입력하고 '드라마 분석 시작' 버튼을 클릭하세요.")