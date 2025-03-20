#!/bin/bash
set -e

echo "서비스 시작 중..."

# AI 서비스 시작
echo "AI 서비스 시작 중..."
cd ai-services
docker compose up -d
echo "AI 서비스가 시작되었습니다."

# 웹 서비스 시작
echo "웹 서비스 시작 중..."
cd ../web-services

# GitHub Pages 셋업 스크립트 실행 (최초 실행 시)
if [ ! -d "site/src" ]; then
  echo "GitHub Pages 기본 셋업 실행 중..."
  bash setup-github-pages.sh
fi

# 컨테이너 시작
docker compose up -d
echo "웹 서비스가 시작되었습니다."

# 서비스 상태 확인
echo "모든 서비스가 시작되었습니다."
docker ps

echo "서비스에 접근하는 방법:"
echo "- 정적 웹사이트: http://localhost:8080"
echo "- N8N: http://localhost:5678"
echo "- Ollama: http://localhost:11434"
echo "- Open WebUI: http://localhost:3000"
echo "- Flowise: http://localhost:3001"
echo "- Qdrant: http://localhost:6333" 