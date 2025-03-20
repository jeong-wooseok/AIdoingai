# AiDoingAi WordPress 웹 서비스

이 저장소는 Docker를 사용하여 WordPress, MariaDB, Nginx 및 SSL 인증서를 포함한 웹 서비스를 쉽게 배포할 수 있는 구성을 제공합니다.

## 요구 사항

- Docker 및 Docker Compose가 설치된 서버
- 도메인이 서버 IP를 가리키도록 설정
- 포트 80 및 443이 열려 있어야 함
- 기본 명령어에 대한 이해

## 설치 및 실행 방법

### 1. 저장소 복제

```bash
git clone https://github.com/jeong-wooseok/aidoingai.git
cd aidoingai/web-services
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 필요한 설정을 변경합니다:

```bash
# 예제 파일을 복사
cp .env.example .env

# 편집기로 .env 파일 열기
nano .env
```

다음 설정을 변경하세요:
- `MYSQL_ROOT_PASSWORD`: MariaDB 루트 비밀번호 (강력한 비밀번호 사용)
- `MYSQL_PASSWORD`: WordPress 데이터베이스 비밀번호 (강력한 비밀번호 사용)
- `WORDPRESS_DB_PASSWORD`: WordPress 데이터베이스 비밀번호 (위와 동일해야 함)
- `DOMAIN_NAME`: 사용할 도메인 이름 (예: aidoingai.com)
- `DOMAIN_WWW`: www 포함된 도메인 이름 (예: www.aidoingai.com)

### 3. Docker Compose 실행

```bash
# 서비스 시작
docker compose up -d
```

### 4. 개발 환경 설정 (로컬 개발 시에만 필요)

로컬 개발 환경에서는 호스트 파일을 수정하여 도메인을 localhost로 연결해야 합니다:

**Windows:**
`C:\Windows\System32\drivers\etc\hosts` 파일에 다음 내용 추가:
```
127.0.0.1 aidoingai.com
127.0.0.1 www.aidoingai.com
```

**Mac/Linux:**
`/etc/hosts` 파일에 다음 내용 추가:
```
127.0.0.1 aidoingai.com
127.0.0.1 www.aidoingai.com
```

### 5. WordPress 초기 설정

브라우저에서 도메인으로 접속하여 WordPress 초기 설정을 완료합니다.

## 구성 요소

- **WordPress**: 콘텐츠 관리 시스템
- **MariaDB**: 데이터베이스
- **Nginx**: 웹 서버 및 프록시
- **SSL 설정**: 자체 서명 인증서 또는 Let's Encrypt 인증서 사용 가능

## 디렉토리 구조

```
web-services/
├── .env                    # 환경 변수 설정
├── .env.example            # 환경 변수 예제 파일
├── docker-compose.yml      # Docker Compose 설정 파일
├── nginx/                  # Nginx 설정 파일
│   ├── conf.d/             # Nginx 서버 설정
│   └── ssl/                # SSL 인증서 디렉토리
├── mariadb/                # MariaDB 데이터 및 설정
│   └── data/               # 데이터베이스 데이터 (자동 생성)
├── wordpress/              # WordPress 파일 (자동 생성)
└── letsencrypt/            # Let's Encrypt 인증서 (선택적)
```

## 주의 사항

- 프로덕션 환경에서는 `.env` 파일의 비밀번호를 강력하게 설정하세요
- 방화벽 설정을 확인하여 필요한 포트만 열려 있는지 확인하세요
- 정기적으로 백업을 수행하세요
- Docker 및 모든 서비스를 최신 상태로 유지하세요

## 문제 해결

**WordPress 연결 오류:**
- 컨테이너 로그 확인: `docker compose logs wordpress`
- MariaDB 컨테이너 실행 상태 확인: `docker compose ps`
- 데이터베이스 설정 확인: `.env` 파일의 데이터베이스 정보

**Nginx 오류:**
- Nginx 로그 확인: `docker compose logs nginx`
- 설정 파일 문법 확인: `docker compose exec nginx nginx -t`

## 배포 시 주의사항

### 민감한 파일 관리

이 프로젝트는 `.gitignore`를 통해 다음과 같은 민감한 파일과 디렉토리를 Git 저장소에서 제외합니다:

- `.env` 파일 (데이터베이스 암호 등 민감한 정보 포함)
- SSL 인증서 및 개인 키
- WordPress 데이터 및 업로드 파일
- 데이터베이스 데이터 디렉토리

새로운 서버에 배포할 때는 반드시 `.env.example` 파일을 참고하여 `.env` 파일을 새로 만들어 주세요.

### 배포 순서

1. 저장소 복제
2. `.env` 파일 설정 (`.env.example` 파일 참고)
3. 컨테이너 시작: `docker compose up -d`
4. 호스트 시스템에서 호스트 파일 수정 (개발 환경에서만 필요)
5. WordPress 초기 설정 완료

### 백업 및 복원

데이터베이스와 WordPress 파일을 정기적으로 백업하는 것이 중요합니다.

#### 데이터베이스 백업
```bash
docker exec mariadb sh -c 'exec mysqldump --all-databases -uroot -p"$MYSQL_ROOT_PASSWORD"' > backup_db_$(date +%Y-%m-%d).sql
```

#### WordPress 파일 백업
```bash
tar -czvf wordpress_backup_$(date +%Y-%m-%d).tar.gz ./wordpress
```

#### 복원 방법
```bash
# 데이터베이스 복원
cat backup_db_YYYY-MM-DD.sql | docker exec -i mariadb sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD"'

# WordPress 파일 복원
tar -xzvf wordpress_backup_YYYY-MM-DD.tar.gz
``` 