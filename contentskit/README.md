# AI하는아이_contentskit

이 프로젝트는 AI 워크플로우를 위한 완전한 셀프 호스팅 환경을 제공하는 Docker Compose 기반 템플릿입니다. 로컬 LLM, 워드프레스 웹사이트, 자동화 워크플로우 등을 쉽게 구축할 수 있습니다.

## 포함된 서비스

✅ **n8n** - 400개 이상의 통합과 고급 AI 컴포넌트를 갖춘 로우코드 플랫폼
✅ **WordPress** - 세계에서 가장 인기 있는 CMS 시스템
✅ **MariaDB** - WordPress를 위한 데이터베이스
✅ **Ollama** - 최신 로컬 LLM을 설치하고 실행하기 위한 크로스 플랫폼 LLM 플랫폼
✅ **Open WebUI** - 로컬 모델과 상호작용할 수 있는 ChatGPT 스타일 인터페이스
✅ **Flowise** - n8n과 잘 어울리는 노코드/로우코드 AI 에이전트 빌더
✅ **Qdrant** - 고성능 벡터 저장소
✅ **Whisper ASR** - 음성 인식 서비스

## 사전 요구 사항

시작하기 전에 다음 소프트웨어가 설치되어 있는지 확인하세요:

- [Docker/Docker Desktop](https://www.docker.com/products/docker-desktop/) - 모든 서비스를 실행하는 데 필요
- [Git](https://git-scm.com/downloads) - 저장소 복제에 필요

## 설치 방법

1. 저장소를 복제하고 프로젝트 디렉토리로 이동합니다:
   ```bash
   git clone https://github.com/jeong-wooseok/AIdoingai.git
   cd contentskit
   ```

2. `sample.env` 파일을 필요한 환경 변수를 설정후 '.env'로 저장합니다:
   ```
   # MariaDB 설정
   MYSQL_ROOT_PASSWORD=안전한_비밀번호로_변경
   WORDPRESS_DB_NAME=wordpress
   WORDPRESS_DB_USER=wordpress
   WORDPRESS_DB_PASSWORD=안전한_비밀번호로_변경

   # PostgreSQL 설정
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=안전한_비밀번호로_변경
   POSTGRES_DB=n8n

   # N8N 설정
   N8N_ENCRYPTION_KEY=안전한_키로_변경
   N8N_USER_MANAGEMENT_JWT_SECRET=안전한_시크릿으로_변경
   ```

3. Docker Compose를 사용하여 서비스를 시작합니다:

   ### NVIDIA GPU 사용자
   ```bash
   docker compose --profile gpu-nvidia up -d
   ```

   ### CPU만 사용하는 경우
   ```bash
   docker compose --profile cpu up -d
   ```

## 서비스 접속 방법

설치가 완료되면 다음 URL을 통해 각 서비스에 접속할 수 있습니다:

- **n8n**: http://localhost:5678/
- **WordPress**: http://localhost:8080/
- **Open WebUI**: http://localhost:3000/
- **Flowise**: http://localhost:3001/

## n8n 초기 설정

1. http://localhost:5678/ 에 접속하여 n8n을 설정합니다. 이는 한 번만 수행하면 됩니다.
2. 계정을 생성하고 로그인합니다.
3. 다음 서비스에 대한 자격 증명을 생성합니다:
   
   - **Ollama URL**: http://ollama:11434
   - **Postgres**: 호스트 - postgres, 사용자 이름/비밀번호 - .env 파일에서 설정한 값
   - **Qdrant URL**: http://qdrant:6333

## WordPress 초기 설정

1. http://localhost:8080/ 에 접속합니다.
2. WordPress 설치 마법사를 따라 사이트를 설정합니다.
3. .env 파일에 설정한 데이터베이스 정보를 입력합니다:
   - 데이터베이스 이름: WORDPRESS_DB_NAME 값
   - 사용자 이름: WORDPRESS_DB_USER 값
   - 비밀번호: WORDPRESS_DB_PASSWORD 값
   - 데이터베이스 호스트: mariadb
   - 테이블 접두사: wp_ (기본값)

## Open WebUI 사용 방법

1. http://localhost:3000/ 에 접속하여 Open WebUI를 설정합니다.
2. 로컬 계정을 생성하고 로그인합니다.
3. Ollama 모델을 선택하여 대화를 시작할 수 있습니다.

## Flowise 사용 방법

1. http://localhost:3001/ 에 접속하여 Flowise를 설정합니다.
2. AI 워크플로우를 생성하고 관리할 수 있습니다.

## 음성 인식 서비스 (Whisper ASR) 사용 방법

Whisper ASR 서비스는 http://localhost:9000/ 에서 실행되며, n8n 워크플로우에서 음성 인식 기능을 사용할 수 있습니다.

Key configuration options:

- `ASR_ENGINE`: Engine selection (openai_whisper, faster_whisper, whisperx)
- `ASR_MODEL`: Model selection (tiny, base, small, medium, large-v3, etc.)
- `ASR_MODEL_PATH`: Custom path to store/load models
- `ASR_DEVICE`: Device selection (cuda, cpu)
- `MODEL_IDLE_TIMEOUT`: Timeout for model unloading

## 서비스 업데이트

모든 컨테이너를 최신 버전으로 업데이트하려면 다음 명령을 실행하세요:

```bash
# 모든 서비스 중지
docker compose down

# 최신 버전의 모든 컨테이너 가져오기
docker compose pull

# 서비스 다시 시작 (원하는 프로필 사용)
docker compose --profile <your-profile> up -d
```

`<your-profile>`을 `cpu`, `gpu-nvidia` 중 하나로 바꾸세요.

## 문제 해결

### GPU 지원 문제

- **Windows GPU 지원**: Docker Desktop에서 Ollama를 GPU 지원으로 실행하는 데 문제가 있는 경우:
  1. Docker Desktop 설정 열기
  2. WSL 2 백엔드 활성화
  3. 자세한 내용은 [Docker GPU 문서](https://docs.docker.com/desktop/features/gpu/)를 참조하세요.

- **Linux GPU 지원**: Linux에서 Ollama를 GPU 지원으로 실행하는 데 문제가 있는 경우, [Ollama Docker 지침](https://github.com/ollama/ollama/blob/main/docs/docker.md)을 따르세요.

### 데이터베이스 문제

- **MariaDB 연결 문제**: WordPress에서 데이터베이스 연결 오류가 발생하는 경우, .env 파일의 자격 증명이 올바른지 확인하고 MariaDB 컨테이너가 실행 중인지 확인하세요.

## 데이터 백업

모든 데이터는 Docker 볼륨에 저장됩니다. 중요한 데이터를 백업하려면 다음 디렉토리를 백업하세요:

- n8n 데이터: `./n8n/backup/`
- WordPress 데이터: `wordpress_data` 볼륨
- MariaDB 데이터: `mariadb_data` 볼륨

## 보안 참고 사항

이 스타터 킷은 개발 및 테스트 환경을 위해 설계되었습니다. 프로덕션 환경에서 사용하기 전에 다음 사항을 고려하세요:

1. `.env` 파일의 모든 비밀번호와 시크릿을 강력한 값으로 변경하세요.
2. 필요한 경우 HTTPS를 구성하세요.
3. 방화벽 규칙을 설정하여 필요한 포트만 노출하세요.