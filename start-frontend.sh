#!/bin/bash

echo "🚀 프론트엔드 서버 시작 중..."

cd frontend

# node_modules가 없으면 설치
if [ ! -d "node_modules" ]; then
    echo "📦 의존성 설치 중..."
    npm install
fi

# 개발 서버 실행
echo "✅ 서버 실행 중..."
echo "📍 웹 앱: http://localhost:3000"
npm run dev
