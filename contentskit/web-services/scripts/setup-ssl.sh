#!/bin/bash
set -e

# 환경 변수 로드
source .env

echo "도메인: $DOMAIN_NAME, $DOMAIN_WWW"
echo "서버 IP: $SERVER_IP"

# 자체 서명 인증서 생성
if [ ! -f "./nginx/conf.d/self-signed.crt" ]; then
    echo "자체 서명 인증서 생성 중..."
    mkdir -p ./nginx/conf.d/
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ./nginx/conf.d/self-signed.key \
        -out ./nginx/conf.d/self-signed.crt \
        -subj "/C=KR/ST=Seoul/L=Seoul/O=AiDoingAi/OU=Blog/CN=$DOMAIN_NAME"
    echo "자체 서명 인증서 생성 완료"
fi

# WordPress DB 설정 업데이트
sleep 10 # MariaDB 시작을 기다림
echo "WordPress 사이트 URL 설정 업데이트 중..."
docker exec -i mariadb mysql -u${WORDPRESS_DB_USER} -p${WORDPRESS_DB_PASSWORD} ${WORDPRESS_DB_NAME} <<EOF
UPDATE wp_options SET option_value='https://${DOMAIN_NAME}' WHERE option_name='siteurl';
UPDATE wp_options SET option_value='https://${DOMAIN_NAME}' WHERE option_name='home';
EOF
echo "WordPress URL 설정 업데이트 완료"

# Let's Encrypt 인증서 발급
echo "Let's Encrypt 인증서 발급을 시작합니다..."
mkdir -p ./nginx/certbot-conf
mkdir -p ./nginx/certbot-www

echo "중요: 인증서 발급을 위해 포트 80이 외부에서 접근 가능해야 합니다."
echo "모든 네트워크 설정이 완료되었고 도메인이 서버 IP($SERVER_IP)를 가리키는지 확인하세요."
read -p "계속하려면 엔터를 누르세요..." 

# 스테이징 모드 설정
if [ "$LETSENCRYPT_STAGING" -eq 1 ]; then
    STAGING_ARG="--staging"
    echo "스테이징 모드로 인증서 발급 (테스트용)"
else
    STAGING_ARG=""
    echo "프로덕션 모드로 인증서 발급"
fi

# Certbot 실행
docker run --rm -it \
    -v $(pwd)/nginx/certbot-conf:/etc/letsencrypt \
    -v $(pwd)/nginx/certbot-www:/var/www/certbot \
    -p 80:80 \
    certbot/certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos --no-eff-email \
    -d $DOMAIN_NAME -d $DOMAIN_WWW \
    $STAGING_ARG

# Nginx 설정 업데이트
echo "Nginx 설정 업데이트 중..."
NGINX_CONF="./nginx/conf.d/default.conf"
sed -i.bak 's|# ssl_certificate /etc/letsencrypt|ssl_certificate /etc/letsencrypt|g' $NGINX_CONF
sed -i.bak 's|# ssl_certificate_key /etc/letsencrypt|ssl_certificate_key /etc/letsencrypt|g' $NGINX_CONF

# Docker 컨테이너 재시작
echo "Docker 컨테이너 재시작 중..."
docker compose restart nginx wordpress

echo "설정 완료! https://$DOMAIN_NAME 으로 접속할 수 있습니다." 