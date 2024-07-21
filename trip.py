from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun
from crewai_tools import DirectoryReadTool,FileReadTool
from langchain.tools.file_management.read import ReadFileTool
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os

load_dotenv()

gpt = ChatOpenAI(model="gpt-4o-mini",
             api_key=os.getenv("OPENAI_API_KEY"), 
             temperature=0,
             max_tokens=4000)

clud = ChatAnthropic(model="claude-3-sonnet-20240229",
                     anthropic_api_key=os.getenv("Anthropic_API_KEY"),
                     temperature=0,
                     max_tokens=4000)

# 도구 초기화
search_tool = DuckDuckGoSearchRun()

# 에이전트 정의
travel_planner = Agent(
    role='여행 계획가',
    goal='고객의 선호도와 예산에 맞는 최적의 여행 계획 수립',
    backstory='15년 경력의 전문 여행 계획가로, 다양한 고객의 요구사항을 만족시키는 맞춤형 여행 계획을 수립합니다.',
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    llm=gpt
)

local_expert = Agent(
    role='도쿄 현지 전문가',
    goal='도쿄의 숨겨진 명소와 현지 문화에 대한 깊이 있는 정보 제공',
    backstory='도쿄에서 10년 이상 거주한 현지 전문가로, 관광객들이 쉽게 접하기 어려운 특별한 경험을 제안합니다.',
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    llm=gpt
)

schedule_optimizer = Agent(
    role='일정 최적화 전문가',
    goal='효율적이고 즐거운 3일 도쿄 여행 일정 최적화',
    backstory='데이터 분석과 여행 경험을 결합하여 고객의 시간과 에너지를 최대한 활용할 수 있는 최적의 일정을 설계합니다.',
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    llm=gpt
)

# 여행 정보 딕셔너리
travel_info = {
    "destination": "일본 도쿄",
    "duration": "3일",
    "travelers": "와이프와 둘이",
    "arrival": "저녁 8시",
    "hotels": {
        "day1": "도세이호텔 코코네우에노",
        "day2_3": "Nippon Seinenkan Hotel Tokyo, Shinjuku"
    },
    "departure": "3일차 저녁 10시",
    "preferences": "유명관광지, 면세 쇼핑, 적절히 맛있는 음식"
}

# 태스크 정의
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
    ''',
    expected_output="고객의 여행 선호도와 제약 사항에 대한 상세한 분석",
    agent=travel_planner
)

task2 = Task(
    description=f'''
    {travel_info['destination']}의 추천 장소와 활동 목록을 작성하세요. 
    특히 {travel_info['preferences']}에 중점을 두고, {travel_info['duration']} 동안 
    {travel_info['travelers']}이 즐길 수 있는 장소를 추천해주세요.
    ''',
    expected_output="도쿄의 추천 장소와 활동 목록 (휴양 및 맛집 중심)",
    agent=local_expert
)

task3 = Task(
    description=f'''
    주어진 정보와 추천 목록을 바탕으로 {travel_info['duration']}간의 세부 여행 일정을 최적화하세요.
    - 도착: {travel_info['arrival']}
    - 1일차 호텔: {travel_info['hotels']['day1']}
    - 2-3일차 호텔: {travel_info['hotels']['day2_3']}
    - 출발: {travel_info['departure']}
    선호사항인 {travel_info['preferences']}을 고려하여 일정을 조정하세요.
    각 동선 별 이동경로, 이동수단을 상세히 알려주세요.
    음식점은 끼니별로 예비후보지 2~3곳도 추가로 알려주세요
    ''',
    expected_output="3일간의 최적화된 세부 여행 일정",
    agent=schedule_optimizer
)

# Crew 생성 및 실행
crew = Crew(
    agents=[travel_planner, local_expert, schedule_optimizer],
    tasks=[task1, task2, task3],
    verbose=1
)

result = crew.kickoff()

print("최종 여행 계획:")
print(result)