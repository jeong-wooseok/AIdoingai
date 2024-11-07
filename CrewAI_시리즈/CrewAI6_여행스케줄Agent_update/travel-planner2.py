import streamlit as st
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
import csv
from typing import Dict, List
from langchain.tools import BaseTool, DuckDuckGoSearchRun
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

load_dotenv()

# 마크다운 텍스트 처리 함수
def process_markdown(text):
    # 줄바꿈을 두 번 하여 마크다운에서 단락으로 인식되도록 함
    return text.replace('\n', '\n\n')


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


class CustomSearchTool(BaseTool):
    name: str = "custom_search"
    description: str = "Searches the internet for recent results."
    search_engine = DuckDuckGoSearchRun()  # 인스턴스화

    def _run(self, query: str) -> str:
        if search_cache.get_search_count(query) >= 3:
            return "검색 횟수 제한에 도달했습니다. 다른 키워드로 검색해 주세요."

        cached_results = search_cache.get(query)
        if cached_results:
            return "\n".join(cached_results)

        # DuckDuckGoSearchRun을 사용한 실제 검색 수행
        search_results = self.search_engine.run(query)

        # 결과를 줄 단위로 분리하고 중복 제거
        results = search_results.split('\n')
        filtered_results = list(set(results))

        # 결과가 너무 길 경우 처음 5개 항목으로 제한
        if len(filtered_results) > 5:
            filtered_results = filtered_results[:5]

        search_cache.add(query, filtered_results)
        return "\n".join(filtered_results)

    def _arun(self, query: str) -> str:
        raise NotImplementedError("CustomSearchTool does not support async")

    # 매개변수를 구체적으로 지정
    def run(self, query: str, **kwargs: Any) -> str:
        return self._run(query)

# 검색 도구 초기화
search_tool = CustomSearchTool()

# 검색 결과 분석 및 요약 함수
def analyze_and_summarize(search_results: str) -> str:
    gpt = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), temperature=0, max_tokens=2000)
    prompt = f"다음 검색 결과를 분석하고 요약해주세요. 중요한 정보만 간결하게 추출하여 3-5개의 핵심 포인트로 정리해주세요:\n\n{search_results}\n\n요약:"
    response = gpt.invoke(prompt)
    return response.content


# Streamlit 페이지 설정
st.set_page_config(page_title="AI 여행 계획 도우미", page_icon="✈️", layout="wide")
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
st.markdown('<p class="big-font">AI 여행 계획 도우미</p>', unsafe_allow_html=True)

# 여행 계획 생성 결과 표시 함수
def display_travel_plan(plan):
    st.markdown('<p class="medium-font">여행 계획 채팅</p>', unsafe_allow_html=True)
    
    # 계획을 줄 단위로 분리하고 각 줄을 적절히 포맷팅
    lines = plan.split('\n')
    for line in lines:
        if line.strip():  # 빈 줄 제외
            if ':' in line:  # 제목이나 시간 정보로 간주
                st.markdown(f'**{line.strip()}**')
            else:
                st.markdown(f'<p class="small-font">{line.strip()}</p>', unsafe_allow_html=True)
        else:
            st.write('')  # 빈 줄 유지

# 사용자 입력
user_input = st.text_input("추가 요청 또는 질문을 입력하세요:")

if user_input:
    st.markdown('<p class="small-font">사용자: {}</p>'.format(user_input), unsafe_allow_html=True)
    # 여기에 AI 응답 로직 추가
    ai_response = "AI의 응답이 여기에 표시됩니다."
    st.markdown('<p class="small-font">AI: {}</p>'.format(ai_response), unsafe_allow_html=True)


# 세션 상태 초기화
if 'travel_plan' not in st.session_state:
    st.session_state.travel_plan = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

gpt = ChatOpenAI(model="gpt-4o-mini",
             api_key=os.getenv("OPENAI_API_KEY"), 
             temperature=0,
             max_tokens=4000)

clud = ChatAnthropic(model="claude-3-5-sonnet-20240620",
                     anthropic_api_key=os.getenv("Anthropic_API_KEY"),
                     temperature=0,
                     max_tokens=4000)

# 링크 생성 및 저장 함수
def generate_and_save_links(travel_plan):
    gpt = ChatOpenAI(model="gpt-4o-mini",
         api_key=os.getenv("OPENAI_API_KEY"), 
         temperature=0,
         max_tokens=4000)
    
    prompt = f"""
    다음 여행 계획을 바탕으로, 여행자에게 유용할 5개의 참고 링크를 생성해주세요.
    각 링크에 대해 질문, 링크 URL, 간단한 요약을 제공해주세요.
    링크는 실제로 존재하는 웹사이트여야 합니다.
    
    여행 계획:
    {travel_plan}
    
    응답 형식:
    1. 질문1
    링크1
    요약1
    
    2. 질문2
    링크2
    요약2
    
    ...
    """
    
    response = gpt.invoke(prompt)
    links_info = response.content.split('\n\n')
    
    with open('reference_links.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['질문', '링크', '요약'])
        
        for info in links_info:
            parts = info.split('\n')
            if len(parts) >= 3:
                question = parts[0].lstrip('123456789. ')
                link = parts[1]
                summary = parts[2]
                writer.writerow([question, link, summary])
    
    st.success("참고 링크가 'reference_links.csv' 파일로 저장되었습니다.")
    return links_info

# 사이드바에 변수 입력 섹션 생성
with st.sidebar:
    st.header("여행 정보 입력")
    destination = st.text_input("여행지", value="일본 오사카")
    duration = st.text_input("여행 기간", value="3일")
    travelers = st.text_input("여행자", value="와이프, 8살딸 포함 세명")
    arrival = st.text_input("도착 시간", value="저녁 8시")
    departure = st.text_input("출발 시간", value="3일차 저녁 10시")
    hotel_day1 = st.text_input("1일차 호텔", value="소테츠 그랜드 프레사 오사카")
    hotel_day2_3 = st.text_input("2-3일차 호텔", value="호텔 한큐 레스파이어 오사카")

    st.subheader("선호도 설정")
    food_preferences = st.multiselect(
        "음식 선호도 (복수 선택 가능)",
        ["일본 전통 요리 (스시, 라멘 등)", "현대적인 퓨전 요리", "길거리 음식", "고급 미슐랭 레스토랑"],
        default=["일본 전통 요리 (스시, 라멘 등)"]
    )
    place_preferences = st.multiselect(
        "장소 분위기 선호도 (복수 선택 가능)",
        ["번화가와 쇼핑 지역", "조용한 주택가와 공원", "역사적인 명소와 신사", "현대적인 건축물과 테크놀로지 중심지"],
        default=["번화가와 쇼핑 지역", "역사적인 명소와 신사"]
    )
    activity_preference = st.selectbox(
        "가장 선호하는 활동",
        ["문화 체험 (예: 다도, 기모노 입기)", "엔터테인먼트 (예: 디즈니랜드, 로봇 레스토랑)", "자연 감상 (예: 공원, 정원)", "쇼핑 (예: 면세점, 백화점)"]
    )

    priority = st.multiselect(
        "선호도 우선순위를 설정해주세요 (순서대로 선택)",
        ["음식", "장소", "활동"],
        default=["음식", "장소", "활동"]
    )
    


    if st.button("여행 계획 생성"):
        travel_info = {
            "destination": destination,
            "duration": duration,
            "travelers": travelers,
            "arrival": arrival,
            "departure": departure,
            "hotels": {
                "day1": hotel_day1,
                "day2_3": hotel_day2_3
            },
            "preferences": {
                "food": [i+1 for i, pref in enumerate(["일본 전통 요리 (스시, 라멘 등)", "현대적인 퓨전 요리", "길거리 음식", "고급 미슐랭 레스토랑"]) if pref in food_preferences],
                "place": [i+1 for i, pref in enumerate(["번화가와 쇼핑 지역", "조용한 주택가와 공원", "역사적인 명소와 신사", "현대적인 건축물과 테크놀로지 중심지"]) if pref in place_preferences],
                "activity": ["문화 체험 (예: 다도, 기모노 입기)", "엔터테인먼트 (예: 디즈니랜드, 로봇 레스토랑)", "자연 감상 (예: 공원, 정원)", "쇼핑 (예: 면세점, 백화점)"].index(activity_preference) + 1
            },
            "weights": {
                "food": 0.5 if priority[0] == "음식" else (0.3 if priority[1] == "음식" else 0.2),
                "place": 0.5 if priority[0] == "장소" else (0.3 if priority[1] == "장소" else 0.2),
                "activity": 0.5 if priority[0] == "활동" else (0.3 if priority[1] == "활동" else 0.2)
            }
        }
              

        travel_planner = Agent(
            role='여행 계획가',
            goal='고객의 선호도와 예산에 맞는 최적의 여행 계획 수립',
            backstory='15년 경력의 전문 여행 계획가로, 다양한 고객의 요구사항을 만족시키는 맞춤형 여행 계획을 수립합니다.',
            verbose=True,
            allow_delegation=False,
            tools=[search_tool],
            llm=clud
        )

        local_expert = Agent(
            role='도쿄 현지 전문가',
            goal='도쿄의 숨겨진 명소와 현지 문화에 대한 깊이 있는 정보 제공',
            backstory='도쿄에서 10년 이상 거주한 현지 전문가로, 관광객들이 쉽게 접하기 어려운 특별한 경험을 제안합니다.',
            verbose=True,
            allow_delegation=False,
            tools=[search_tool],
            llm=gpt
        )

        schedule_optimizer = Agent(
            role='일정 최적화 전문가',
            goal='효율적이고 즐거운 3일 도쿄 여행 일정 최적화',
            backstory='데이터 분석과 여행 경험을 결합하여 고객의 시간과 에너지를 최대한 활용할 수 있는 최적의 일정을 설계합니다.',
            verbose=True,
            allow_delegation=False,
            tools=[search_tool],
            llm=clud
        )

        task1 = Task(
            description=f'''
            다음 여행 정보를 분석하고 고객의 선호도와 제약 사항을 파악하세요:
            - 목적지: {travel_info['destination']}
            - 기간: {travel_info['duration']}
            - 여행자: {travel_info['travelers']}
            - 도착 시간: {travel_info['arrival']}
            - 호텔: 1일차 {travel_info['hotels']['day1']}, 2-3일차 {travel_info['hotels']['day2_3']}
            - 출발 시간: {travel_info['departure']}
            - 선호사항: {travel_info['preferences']}
            - 가중치: {travel_info['weights']}
            고객의 선호도와 가중치를 고려하여 여행의 우선순위를 결정하세요.
            복수 선택된 음식과 장소 선호도에 대해 다양한 옵션을 제공하세요.
            최종결과를 한국어로 번역해주세요.
            ''',
            expected_output="고객의 여행 선호도와 제약 사항에 대한 상세한 분석, 우선순위가 반영된 계획 방향",
            agent=travel_planner
        )

        task2 = Task(
            description=f'''
            {travel_info['destination']}의 추천 장소와 활동 목록을 작성하세요. 
            다음 선호도와 가중치를 고려하여 {travel_info['duration']} 동안 
            {travel_info['travelers']}이 즐길 수 있는 장소를 추천해주세요:
            - 선호사항: {travel_info['preferences']}
            - 가중치: {travel_info['weights']}
            선택된 장소에 방문전 필수로 알아야 하는 TIP에 대해 정리해주세요
            최종결과를 한국어로 번역해주세요.
            ''',
            expected_output="도쿄 추천장소 목록, 방문전 필수Tip, 추천장소 별 활동 목록 (고객 선호도와 우선순위 반영)",
            agent=local_expert
        )

        task3 = Task(
            description=f'''
            주어진 정보와 추천 목록을 바탕으로 {travel_info['duration']}간의 세부 여행 일정을 최적화하세요.
            - 도착: {travel_info['arrival']}
            - 1일차 호텔: {travel_info['hotels']['day1']}
            - 2-3일차 호텔: {travel_info['hotels']['day2_3']}
            - 출발: {travel_info['departure']}
            다음 선호사항과 가중치를 고려하여 일정을 조정하세요:
            - 선호사항: {travel_info['preferences']}
            - 가중치: {travel_info['weights']}
            가중치가 높은 활동에 더 많은 시간을 할당하고, 각 동선별 이동경로와 이동수단을 상세히 알려주세요.
            복수 선택된 음식과 장소 선호도를 고려하여 다양한 경험을 제공하세요.
            음식점은 끼니별로 예비후보지 2~3곳도 추가로 알려주세요.
            최종결과를 한국어로 번역해주세요.
            ''',
            expected_output="3일간의 최적화된 세부 여행 일정 (우선순위와 가중치 반영), 장소별 음식점 예비후보지 2~3곳",
            agent=schedule_optimizer
        )

        crew = Crew(
            agents=[travel_planner, local_expert, schedule_optimizer],
            tasks=[task1, task2, task3],
            verbose=2
        )

        with st.spinner('여행 계획을 생성 중입니다...'):
            progress_placeholder = st.empty()
            result = ""
            for step, agent_response in enumerate(crew.kickoff()):
                result += agent_response + "\n"
                progress_placeholder.info(f"진행 중: {step+1}/3 단계 완료")
                st.markdown(process_markdown(agent_response))
            
            st.success("여행 계획 생성이 완료되었습니다!")
            st.session_state.travel_plan = result
            st.session_state.chat_history.append(("AI", result))
        
            # 참고 링크 생성 및 저장
            st.info("참고 링크를 생성 중입니다...")
            links_info = generate_and_save_links(result)
        
            # 참고 링크 표시
            st.subheader("참고할 만한 링크")
            for info in links_info:
                parts = info.split('\n')
                if len(parts) >= 3:
                    st.markdown(f"**{parts[0]}**")
                    st.markdown(f"링크: {parts[1]}")
                    st.markdown(f"요약: {parts[2]}")
                    st.markdown("---")

# 메인 화면에 채팅 섹션 생성
st.header("여행 계획 채팅")

# 채팅 기록 표시
for role, message in st.session_state.chat_history:
    if role == "Human":
        st.markdown(f"**You:** {process_markdown(message)}")
    else:
        st.markdown(f"**AI:** {process_markdown(message)}")



if user_input:
    st.session_state.chat_history.append(("Human", user_input))
    
    # AI 응답 생성
    gpt = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), temperature=0, max_tokens=4000)
    
    response = gpt.invoke(f"""사용자의 요청: {user_input}
    
    기존 여행 계획:
    {st.session_state.travel_plan}
    사용자의 요청을 반영하여 여행 계획을 수정하거나 추가 정보를 제공해주세요. 응답은 한국어로 해주세요.""")
    
    ai_response = response.content
    st.session_state.chat_history.append(("AI", ai_response))
    st.markdown(f"**AI:** {process_markdown(ai_response)}")

# 채팅 기록 및 최종 계획 저장
if st.button("채팅 기록 및 최종 계획 저장"):
    # travel_plan_chat.txt 파일 저장
    with open("travel_plan_chat.txt", "w", encoding="utf-8-sig") as f:
        for role, message in st.session_state.chat_history:
            f.write(f"{role}: {message}\n\n")
    
    # 최종 여행 계획 저장
    if st.session_state.travel_plan:
        with open("final_travel_plan.txt", "w", encoding="utf-8-sig") as f:
            f.write(st.session_state.travel_plan)
    
    st.success("채팅 기록이 'travel_plan_chat.txt' 파일로 저장되었습니다.")
    if st.session_state.travel_plan:
        st.success("최종 여행 계획이 'final_travel_plan.txt' 파일로 저장되었습니다.")

# 저장된 파일 다운로드 버튼 추가
if os.path.exists("travel_plan_chat.txt"):
    with open("travel_plan_chat.txt", "r", encoding="utf-8-sig") as file:
        st.download_button(
            label="채팅 기록 다운로드",
            data=file.read(),
            file_name="travel_plan_chat.txt",
            mime="text/plain"
        )

if os.path.exists("final_travel_plan.txt"):
    with open("final_travel_plan.txt", "r", encoding="utf-8-sig") as file:
        st.download_button(
            label="최종 여행 계획 다운로드",
            data=file.read(),
            file_name="final_travel_plan.txt",
            mime="text/plain"
        )

if os.path.exists("reference_links.csv"):
    with open("reference_links.csv", "r", encoding="utf-8-sig") as file:
        st.download_button(
            label="참고 링크 다운로드",
            data=file.read(),
            file_name="reference_links.csv",
            mime="text/csv"
        )