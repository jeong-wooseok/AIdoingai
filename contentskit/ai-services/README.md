# ContentsKit AI 서비스

ContentsKit의 AI 서비스 컴포넌트로, 동영상 편집 및 처리를 위한 다양한 도구와 워크플로우를 제공합니다.

## 주요 기능

- 동영상 다운로드 (yt-dlp)
- 음성 인식 및 자막 생성 (Whisper ASR)
- 워크플로우 자동화 (n8n)

## 설치 방법

### 사전 요구사항

- Docker 및 Docker Compose 설치
- NVIDIA GPU 및 드라이버 (GPU 가속 사용 시)

### 설치 단계

1. 저장소 클론
   ```bash
   git clone https://github.com/yourusername/contentskit.git
   cd contentskit/ai-services
   ```

2. 환경 변수 설정
   ```bash
   cp .env.example .env
   # .env 파일을 적절히 수정
   ```

3. 서비스 실행
   ```bash
   # CPU 모드
   docker compose --profile cpu up -d
   
   # GPU 모드 (NVIDIA)
   docker compose --profile gpu-nvidia up -d
   ```

## 서비스 구성

### Docker 컨테이너

- **n8n**: 워크플로우 자동화 엔진
- **whisper-asr**: 음성 인식 및 자막 생성 서비스
- **ollama**: 로컬 LLM 실행 엔진
- **qdrant**: 벡터 데이터베이스
- **postgres**: n8n의 데이터베이스
- **flowise**: 플로우 기반 AI 파이프라인
- **open-webui**: Ollama 모델 관리 웹 인터페이스

### 접속 정보

- n8n: http://localhost:5678
- Flowise: http://localhost:3001
- Open WebUI: http://localhost:3000
- Qdrant: http://localhost:6333
- Whisper ASR: http://localhost:9000

## 폴더 및 파일 설명

- **workflow/**: n8n 워크플로우 정의 파일
- **videos/**: 처리할 비디오 파일 및 출력 저장 위치
- **Dockerfile.n8n**: n8n 컨테이너 빌드 정의 파일
- **docker-compose.yml**: 컨테이너 구성 정의 파일
- **auto-editor.md**: auto-editor 도구 사용법
- **auto-editor-usage.md**: auto-editor 사용 예시 및 팁
- **ffmpeg-usage.md**: ffmpeg 명령어 사용 예시
- **.env**: 환경 변수 설정 파일
- **.env.example**: 환경 변수 예시 파일

## 사용 방법

### 비디오 자동 편집

1. 비디오 파일을 `videos/` 디렉토리에 업로드
2. n8n 워크플로우를 통해 처리하거나 수동으로 명령어 실행:

   ```bash
   # 컨테이너 내부에서 auto-editor 실행
   docker exec -it n8n /usr/local/bin/auto_edit.py /data/videos/input.mp4 /data/videos/output.mp4
   ```

### YouTube 비디오 다운로드 및 편집

```bash
# 컨테이너 내부에서 실행
docker exec -it n8n bash -c 'cd /data/videos && yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID" -o "%(title)s.%(ext)s" && /usr/local/bin/auto_edit.py "*.mp4" "edited_*.mp4"'
```

## 문제 해결

- **auto-editor 실행 오류**: 백업 스크립트인 auto-edit.sh가 자동으로 사용됩니다.
- **GPU 인식 문제**: NVIDIA 드라이버와 Docker의 nvidia-container-toolkit이 올바르게 설치되었는지 확인하세요.
- **포트 충돌**: docker-compose.yml 파일에서 포트 매핑을 변경할 수 있습니다.

## 참고 문서

- [n8n 공식 문서](https://docs.n8n.io/)
- [auto-editor 사용법](https://auto-editor.com)
- [Whisper ASR 문서](https://github.com/openai/whisper)
- [Ollama 문서](https://ollama.ai/) 