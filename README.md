# AI하는 ai

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

- 내가 직접 만드는 AGI, Crew AI를 활용해서 Multi Agent를 만들어봐요 (24년 5~6월)
    - 1. [Intro](https://github.com/jeong-wooseok/AIdoingai/blob/main/1%EA%B0%95/Create%20Agents%20to%20Research%20and%20Write%20an%20Article_jeong.ipynb)  &&  [Youtube](https://youtu.be/QKjNmGM_LFw?si=lBYAkc0bOtpLIbYM)
    - 2. [QA 통해서 답변의 퀄러티를 높이고, Tool을 활용하여 인터넷검색까지?](https://github.com/jeong-wooseok/AIdoingai/blob/main/CrewAI2_%EB%82%98%EB%A7%8C%EC%9D%98Agent%EB%A7%8C%EB%93%A4%EA%B8%B0/2%EA%B0%95_jeong.ipynb) &&  [Youtube](https://www.youtube.com/watch?v=Lv2ScMY6JWA)
    - 3. [CrewAI 실전프로젝트, 직접 Tool을 만들어서 넣어봐요. 제휴이메일을 써주는 Multi-Agent](https://github.com/jeong-wooseok/AIdoingai/blob/main/CrewAI3_%EC%97%85%EB%AC%B4%EC%A0%9C%ED%9C%B4%EC%9D%B4%EB%A9%94%EC%9D%BCAgent/3%EA%B0%95_jeong.ipynb) &&  [Youtube](https://www.youtube.com/watch?v=QCr2a8qmVtE)
    - 4. [CrewAI 실전프로젝트, 주식 종목을 추천해주는 Agent, yfinance라이브러리 활용하기, claude-sonnet3.5활용](https://github.com/jeong-wooseok/AIdoingai/blob/main/CrewAI4_%EC%A3%BC%EC%8B%9D%ED%88%AC%EC%9E%90%EC%A0%84%EB%9E%B5Agent/4%EA%B0%95_jeong.ipynb) &&  [Youtube](https://www.youtube.com/watch?v=5Hpvhq2heRw)
- 퀀트 프로젝트 (24년 6월 ~ 8월)
    - 1. [크롤링 기초부터 응용까지 : get, push, selenium, 정규표현식](https://github.com/jeong-wooseok/AIdoingai/blob/main/Quant1_%ED%81%AC%EB%A1%A4%EB%A7%81/%ED%81%AC%EB%A1%A4%EB%A7%81%EA%B8%B0%EC%B4%88%EB%B6%80%ED%84%B0%EC%9D%91%EC%9A%A9%EA%B9%8C%EC%A7%80.ipynb) &&  [Youtube](https://youtu.be/6QljRIThROU)
    - 2. 국내 주식데이터 수집
    - 3. 투자 참고용 데이터 수집
    - 4. 포트폴리오 구성, 백테스트
    - 5. 증권사 API 연결과 매매하기
- 2차 Langchain, Langgraph를 이용한 나만의 채팅서비스 구축 (24년 8~9월)
    - 1. Intro / Model IO / Format / Retriever 과 친해지기
    - 2. Langgraph 친해지기 : 실습과제 진행
    - 3. Memory / Chain을 이용하여 채팅서비스 구성해보기 (Chainlit, streamlit)
    - 3. 건강한 몸을 되찾기위한 30일 작전, 식단관리 대시보드
