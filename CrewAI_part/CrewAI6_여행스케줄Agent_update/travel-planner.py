import streamlit as st
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os

load_dotenv()

# Streamlit 앱 설정
st.set_page_config(page_title="AI 여행 계획 도우미", page_icon="✈️", layout="wide")
st.title("AI 여행 계획 도우미")

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

# 사이드바에 변수 입력 섹션 생성
with st.sidebar:
    st.header("여행 정보 입력")
    destination = st.text_input("여행지", value="일본 오사카")
    duration = st.text_input("여행 기간", value="3일")
    travelers = st.text_input("여행자", value="와이프, 8살딸 포함 세명")
    arrival = st.text_input("도착 시간", value="저녁 8시")
    departure = st.text_input("출발 시간", value="3일차 저녁 10시")
    hotel_day1 = st.text_input("1일차 호텔", value="소테츠 그랜드 프레사 오사카")
    hotel_day2_3 = st.text_input("나머지기간 호텔", value="호텔 한큐 레스파이어 오사카")

    st.subheader("선호도 설정")
    food_preferences = st.multiselect(
        "음식 선호도 (복수 선택 가능)",
        [f"전통 요리", "현대적인 퓨전 요리", "길거리 음식", "고급 미슐랭 레스토랑"],
        default=[f"전통 요리"]
    )
    place_preferences = st.multiselect(
        "장소 분위기 선호도 (복수 선택 가능)",
        ["번화가와 쇼핑 지역", "조용한 주택가와 공원", "역사적인 명소", "현대적인 건축물과 테크놀로지 중심지"],
        default=["번화가와 쇼핑 지역", "역사적인 명소"]
    )
    activity_preference = st.selectbox(
        "가장 선호하는 활동",
        ["문화 체험", "엔터테인먼트 (예: 놀이동산, 로봇 레스토랑)", "자연 감상 (예: 공원, 정원)", "쇼핑 (예: 면세점, 백화점)"]
    )

    priority = st.multiselect(
        "선호도 우선순위를 설정해주세요 (순서대로 선택)",
        ["음식", "장소", "활동"],
        default=["장소", "음식", "활동"]
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
                "other_days": hotel_day2_3
            },
            "preferences": {
                "food": [i+1 for i, pref in enumerate([f"전통 요리", "현대적인 퓨전 요리", "길거리 음식", "고급 미슐랭 레스토랑"]) if pref in food_preferences],
                "place": [i+1 for i, pref in enumerate(["번화가와 쇼핑 지역", "조용한 주택가와 공원", "역사적인 명소", "현대적인 건축물과 테크놀로지 중심지"]) if pref in place_preferences],
                "activity": ["문화 체험", "엔터테인먼트 (예: 놀이공원, 로봇 레스토랑)", "자연 감상 (예: 공원, 정원)", "쇼핑 (예: 면세점, 백화점)"].index(activity_preference) + 1
            },
            "weights": {
                "food": 0.5 if priority[0] == "음식" else (0.3 if priority[1] == "음식" else 0.2),
                "place": 0.5 if priority[0] == "장소" else (0.3 if priority[1] == "장소" else 0.2),
                "activity": 0.5 if priority[0] == "활동" else (0.3 if priority[1] == "활동" else 0.2)
            }
        }


        search_tool = DuckDuckGoSearchRun()

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
            role=f"{travel_info['destination']}의 현지 전문가",
            goal=f"{travel_info['destination']}의 숨겨진 명소와 현지 문화에 대한 깊이 있는 정보 제공",
            backstory=f"{travel_info['destination']}에서 10년 이상 거주한 현지 전문가로, 관광객들이 쉽게 접하기 어려운 특별한 경험을 제안합니다.",
            verbose=True,
            allow_delegation=False,
            tools=[search_tool],
            llm=gpt
        )

        schedule_optimizer = Agent(
            role='일정 최적화 전문가',
            goal=f"효율적이고 즐거운 {travel_info['destination']} 여행 일정 최적화",
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
            - 호텔: 1일차 {travel_info['hotels']['day1']}, 나머지기간 {travel_info['hotels']['other_days']}
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
            expected_output= f"{travel_info['destination']}의 추천장소 목록, 방문전 필수Tip, 추천장소 별 활동 목록 (고객 선호도와 우선순위 반영)",
            agent=local_expert
        )

        task3 = Task(
            description=f'''
            주어진 정보와 추천 목록을 바탕으로 {travel_info['duration']}간의 세부 여행 일정을 최적화하세요.
            - 도착: {travel_info['arrival']}
            - 1일차 호텔: {travel_info['hotels']['day1']}
            - 나머지기간 호텔: {travel_info['hotels']['other_days']}
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
            verbose=1
        )

        with st.spinner('여행 계획을 생성 중입니다...최초 생성에는 약5분이 소요됩니다'):
            result = crew.kickoff()
            st.session_state.travel_plan = result
            st.session_state.chat_history.append(("AI", result))

# 채팅 기록 표시
for role, message in st.session_state.chat_history:
    if role == "Human":
        st.write(f"You: {message}")
    else:
        st.write(f"AI: {message}")

# 사용자 입력
user_input = st.text_input("추가 요청 또는 질문을 입력하세요:")

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
    st.write(f"AI: {ai_response}")

# 채팅 기록 및 최종 계획 저장
if st.button("채팅 기록 및 최종 계획 저장"):
    with open("travel_plan_chat.md", "w", encoding="utf-8") as f:
        for role, message in st.session_state.chat_history:
            f.write(f"{role}: {message}\n\n")
    st.success("채팅 기록 및 최종 계획이 'travel_plan_chat.md' 파일로 저장되었습니다.")