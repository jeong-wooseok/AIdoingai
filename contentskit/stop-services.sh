#!/bin/bash
set -e

echo "서비스 중지 중..."

# 웹 서비스 중지
echo "웹 서비스 중지 중..."
cd web-services
docker compose down
echo "웹 서비스가 중지되었습니다."

# AI 서비스 중지
echo "AI 서비스 중지 중..."
cd ../ai-services
docker compose down
echo "AI 서비스가 중지되었습니다."

echo "모든 서비스가 중지되었습니다." 