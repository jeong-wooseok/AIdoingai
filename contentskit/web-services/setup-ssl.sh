#!/bin/bash
set -e

# 환경 변수 로드
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "오류: .env 파일을 찾을 수 없습니다."
  exit 1
fi

# 필요한 디렉토리 생성
mkdir -p nginx/ssl
mkdir -p nginx/certbot-conf
mkdir -p nginx/certbot-www

# 자체 서명 인증서 생성
echo "자체 서명 SSL 인증서 생성 중..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/self-signed.key \
  -out nginx/ssl/self-signed.crt \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=AI Doing AI/CN=${DOMAIN_NAME}"

echo "자체 서명 인증서가 생성되었습니다."
echo "위치: nginx/ssl/self-signed.crt 및 nginx/ssl/self-signed.key"

# 도메인과 서버 IP 표시
echo "도메인: $DOMAIN_NAME"
echo "서버 IP: $SERVER_IP"

# WordPress URL 설정 업데이트
echo "WordPress URL 설정 업데이트 중..."
docker exec -it wordpress wp option update siteurl "https://${DOMAIN_NAME}" --allow-root
docker exec -it wordpress wp option update home "https://${DOMAIN_NAME}" --allow-root

# Let's Encrypt 인증서 발급 준비
echo "Let's Encrypt 인증서 발급 준비 중..."
echo "먼저 서버의 포트 80이 외부에서 접근 가능한지 확인하세요."
echo "계속하려면 엔터를 누르세요. 취소하려면 Ctrl+C를 누르세요."
read -p ""

# Let's Encrypt 인증서 발급
echo "Let's Encrypt 인증서 발급 중..."
staging_arg=""
if [ "$LETSENCRYPT_STAGING" = "1" ]; then
  echo "주의: 테스트 모드에서 인증서를 발급합니다."
  staging_arg="--staging"
fi

docker run --rm -it \
  -v $PWD/nginx/certbot-conf:/etc/letsencrypt \
  -v $PWD/nginx/certbot-www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  $staging_arg \
  --email $EMAIL \
  -d $DOMAIN_NAME -d $DOMAIN_WWW \
  --agree-tos --force-renewal

# 컨테이너 재시작
echo "Nginx 및 WordPress 컨테이너 재시작 중..."
docker compose restart nginx wordpress

echo "설정이 완료되었습니다. https://${DOMAIN_NAME} 에서 접속 가능합니다." 