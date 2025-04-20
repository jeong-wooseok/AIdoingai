import os
import whisper
import torch
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# 환경 변수에서 모델 크기 가져오기 (기본값: "base")
MODEL_SIZE = os.getenv("ASR_MODEL", "base")
print(f"Loading Whisper model: {MODEL_SIZE}")

# GPU 사용 가능 여부 확인
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

# FastAPI 앱 초기화
app = FastAPI(
    title="Whisper ASR API",
    description="Speech-to-Text API using OpenAI's Whisper model",
    version="1.0.0"
)

# 시작 시 모델 로드
try:
    model = whisper.load_model(MODEL_SIZE).to(DEVICE)
    print(f"Model loaded successfully to {DEVICE}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.get("/")
def read_root():
    return {"message": "Whisper ASR API is running", "model": MODEL_SIZE, "device": DEVICE}

@app.post("/asr")
async def transcribe_audio(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
            content = await file.read()
            temp.write(content)
            temp_path = temp.name
        
        # Whisper로 음성 인식 수행
        print(f"Processing file: {file.filename}")
        result = model.transcribe(temp_path)
        
        # 임시 파일 삭제
        os.unlink(temp_path)
        
        print(f"Transcription successful, result length: {len(result['text'])}")
        return JSONResponse(content={"text": result["text"]})
    
    except Exception as e:
        print(f"Error during transcription: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000) 