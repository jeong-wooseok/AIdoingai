#!/bin/bash
set -e

# 필요한 디렉토리 생성
mkdir -p ./nginx/conf.d
mkdir -p ./nginx/certbot-conf
mkdir -p ./nginx/certbot-www
mkdir -p ./wordpress
mkdir -p ./db_data

# 권한 설정
chmod +x ./scripts/setup-ssl.sh

# 자체 서명 인증서 생성 (SSL 설정 전에 필요)
if [ ! -f "./nginx/conf.d/self-signed.crt" ]; then
    echo "자체 서명 인증서 생성 중..."
    source .env
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ./nginx/conf.d/self-signed.key \
        -out ./nginx/conf.d/self-signed.crt \
        -subj "/C=KR/ST=Seoul/L=Seoul/O=AiDoingAi/OU=Blog/CN=$DOMAIN_NAME"
    echo "자체 서명 인증서 생성 완료"
fi

# Docker Compose 시작
echo "컨테이너 시작 중..."
docker compose up -d

echo "서비스 시작 완료!"
echo "WordPress 설치를 위해 http://<서버IP>로 접속하세요."
echo "SSL 인증서를 설정하려면 ./scripts/setup-ssl.sh 스크립트를 실행하세요." 