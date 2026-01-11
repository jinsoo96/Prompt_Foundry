#!/bin/bash

echo "🚀 백엔드 서버 시작 중..."

cd backend

# 가상환경이 없으면 생성
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
echo "🔧 가상환경 활성화..."
source venv/bin/activate

# 의존성 설치
echo "📥 의존성 설치 중..."
pip install -r requirements.txt

# 서버 실행
echo "✅ 서버 실행 중..."
echo "📍 API 서버: http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
