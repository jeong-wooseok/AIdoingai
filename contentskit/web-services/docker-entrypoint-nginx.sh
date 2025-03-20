#!/bin/bash
set -e

# 환경 변수 확인
echo "도메인: ${DOMAIN_NAME}"
echo "WWW 도메인: ${DOMAIN_WWW}"

# 템플릿에서 설정 파일 생성
envsubst '${DOMAIN_NAME} ${DOMAIN_WWW}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# SSL 인증서 확인
if [ -f "/etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem" ]; then
  echo "Let's Encrypt 인증서를 찾았습니다. SSL 설정을 적용합니다."
  sed -i 's|# ssl_certificate /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem;|ssl_certificate /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem;|g' /etc/nginx/conf.d/default.conf
  sed -i 's|# ssl_certificate_key /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem;|ssl_certificate_key /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem;|g' /etc/nginx/conf.d/default.conf
else
  echo "Let's Encrypt 인증서를 찾을 수 없습니다. 자체 서명 인증서를 사용합니다."
  echo "인증서를 발급하려면 setup-ssl.sh 스크립트를 실행하세요."
fi

# 로그 디렉토리 권한 확인
if [ ! -w "/var/log/nginx" ]; then
    echo "Nginx 로그 디렉토리에 쓰기 권한이 없습니다. 권한을 수정합니다."
    mkdir -p /var/log/nginx
    chmod -R 755 /var/log/nginx
fi

# 정적 사이트 디렉토리 확인
if [ ! -f "/usr/share/nginx/html/index.html" ]; then
    echo "기본 페이지가 없습니다. 간단한 페이지를 생성합니다."
    echo "<html><body><h1>AI Doing AI</h1><p>정적 사이트 설정이 필요합니다.</p></body></html>" > /usr/share/nginx/html/index.html
fi

# 정적 사이트 컨테이너 확인
echo "정적 사이트 컨테이너 확인 중..."
count=0
max_retry=5
until [ $count -ge $max_retry ]
do
    if wget --spider --quiet http://static-site:8080 2>/dev/null; then
        echo "정적 사이트 서비스가 확인되었습니다."
        break
    fi
    count=$((count+1))
    echo "정적 사이트가 아직 준비되지 않았습니다. ($count/$max_retry) 3초 후 다시 시도합니다..."
    sleep 3
done

# Nginx 설정 파일 테스트
echo "Nginx 설정 파일 테스트 중..."
nginx -t

echo "Nginx 서비스 시작..."
exec "$@" 