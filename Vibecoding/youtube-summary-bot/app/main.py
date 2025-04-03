from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import pathlib
from .services.youtube_service import get_video_transcript
from .services.summary_service import generate_summary_openai, generate_summary_gemini

# 프로젝트 루트 디렉토리 찾기
root_dir = pathlib.Path(__file__).parent.parent
env_path = root_dir / '.env'

# .env 파일 로드
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="YouTube Summary Bot",
    description="YouTube 영상의 내용을 자동으로 요약해주는 API",
    version="1.0.0"
)

class VideoRequest(BaseModel):
    url: str
    model_type: str

class SummaryResponse(BaseModel):
    title: str
    summary: str
    key_points: List[str]

@app.post("/summarize", response_model=SummaryResponse)
async def summarize_video(video: VideoRequest):
    try:
        # API 키 확인
        if video.model_type == "OpenAI GPT-4o-mini":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise HTTPException(status_code=400, detail="OpenAI API 키가 설정되어 있지 않습니다.")
        else:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise HTTPException(status_code=400, detail="Google API 키가 설정되어 있지 않습니다.")

        # 자막 추출
        transcript = await get_video_transcript(video.url)
        
        # 모델에 따른 요약 생성
        if video.model_type == "OpenAI GPT-4o-mini":
            summary_result = await generate_summary_openai(transcript, api_key)
        else:
            summary_result = await generate_summary_gemini(transcript, api_key)
        
        return SummaryResponse(
            title=summary_result["title"],
            summary=summary_result["summary"],
            key_points=summary_result["key_points"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "YouTube Summary Bot API에 오신 것을 환영합니다!"} 