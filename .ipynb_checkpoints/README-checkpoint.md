﻿# AI하는 ai

의 공식 github입니다.


AI하는 ai는 최신 트랜드의 기술을 활용하여 "함께" Toy Project를 만들어가는 채널입니다.

- [OPEN API key 생성 바로가기](https://platform.openai.com/api-keys)
- [GROQ API key 생성 바로가기](https://console.groq.com/keys)

다음 명령어를 사용하여 crewai, crewai_tools 및 langchain_community 패키지를 설치할 수 있습니다.

- 가상환경만들기 및 실행하기
```
conda create -n crewai python=3.10
conda activate crewai
pip install crewai==0.28.8 crewai_tools==0.1.6 langchain_community==0.0.29 langchain_openai ipykernel langchain python-dotenv
python -m ipykernel install --user --name=crewai
```

- api키를 저장 후 .env파일을 만들어서 디렉토리에 보관하세요

- 1차 [내가 직접 만드는 AGI, Crew AI를 활용해서 Multi Agent를 만들어봐요 (24년 5월)
    - 1. [Intro](https://github.com/jeong-wooseok/AIdoingai/blob/main/1%EA%B0%95/Create%20Agents%20to%20Research%20and%20Write%20an%20Article_jeong.ipynb)  &&  [Youtube](https://youtu.be/QKjNmGM_LFw?si=lBYAkc0bOtpLIbYM)
    - 2. QA 통해서 답변의 퀄러티를 높이고, Tool을 활용하여 인터넷검색까지?
    - 3. CrewAI 실전프로젝트, 연구 및 기사 작성을 위한 에이전트 생성 
- 2차 Langchain을 이용한 나만의 채팅서비스 구축 (24년 6월)
    - 1. Intro / Model IO / Format / Retriever 과 친해지기
    - 2. Memory / Chain을 이용하여 채팅서비스 구성해보기 (Chainlit)
    - 3. 오늘의 주식분석 레포트 봇, 믿지는 마세요
- 3차 Streamlit을 활용한 대시보드 서비스 만들기  (24년 7월)
    - 1. intro / Streamlit 서비스 이해하기
    - 2. 세부 기능과 친해지기
    - 3. 건강한 몸을 되찾기위한 30일 작전, 식단관리 대시보드
