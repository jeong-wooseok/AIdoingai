# ContentsKit

AI 서비스와 웹 서비스를 위한 Docker Compose 기반 시스템입니다.

## 시스템 구조

이 시스템은 두 개의 주요 서비스 그룹으로 구성됩니다:

### 1. AI 서비스 그룹
- **위치**: `ai-services/`
- **서비스**:
  - n8n: 워크플로우 자동화
  - qdrant: 벡터 데이터베이스
  - postgres: n8n을 위한 데이터베이스
  - open-webui: AI 웹 인터페이스
  - whisper-asr: 음성 인식
  - flowise: 워크플로우 도구
  - ollama: 로컬 LLM 실행 (CPU/GPU 옵션)

### 2. 웹 서비스 그룹
- **위치**: `web-services/`
- **서비스**:
  - wordpress: 콘텐츠 관리 시스템
  - nginx: 웹 서버 및 리버스 프록시
  - mariadb: WordPress 데이터베이스

## 설치 및 실행

### 전체 시스템 시작
```bash
bash start-services.sh
```

### 전체 시스템 중지
```bash
bash stop-services.sh
```

### AI 서비스만 시작하기
```bash
cd ai-services
docker compose up -d
```

### 웹 서비스만 시작하기
```bash
cd web-services
docker compose up -d
```

## SSL 설정

웹 서비스의 SSL 설정 및 도메인 연결을 위해:

```bash
cd web-services
bash setup-ssl.sh
```

## 포트 정보

- WordPress 직접 접속: `9080` 포트
- Nginx 프록시 접속: `8081` 포트 
- HTTPS 접속: `443` 포트
- n8n: `5678` 포트
- flowise: `3001` 포트
- open-webui: `3000` 포트
- whisper-asr: `9000` 포트
- ollama API: `11434` 포트
- qdrant: `6333` 포트

## 환경 설정

각 서비스 그룹은 자체 `.env` 파일을 사용합니다:
.envself 파일을 수정하여 사용하세요

- AI 서비스 환경 설정: `ai-services/.env`
- 웹 서비스 환경 설정: `web-services/.env`

## 주요 기능

- **WordPress (HTTPS)**: 콘텐츠 관리 시스템
- **자동 비디오 편집**: 무음 구간을 제거하는 auto-editor 도구
- **AI 워크플로우**: n8n을 통한 자동화 워크플로우
- **데이터베이스**: MariaDB를 통한 데이터 관리

## 문제 해결

에러가 발생할 경우 아래 로그를 확인하세요:

```
# Nginx 에러 로그
docker exec -it nginx cat /var/log/nginx/error.log

# WordPress 로그
docker exec -it wordpress cat /var/www/html/wp-content/debug.log
```

## 주의사항

- 초기 접속 시 자체 서명된 SSL 인증서를 사용하므로 브라우저에서 보안 경고가 표시될 수 있습니다. "고급" 또는 "진행" 옵션을 선택하여 계속 진행하세요.
- 프로덕션 환경에서는 Let's Encrypt와 같은 서비스를 통해 신뢰할 수 있는 SSL 인증서를 설정하는 것이 좋습니다.