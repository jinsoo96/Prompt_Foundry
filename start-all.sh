#!/bin/bash

set -euo pipefail

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

echo "백엔드 + 프론트엔드 동시 시작..."

# .env 파일에서 LLM_PROVIDER 확인
if [ -f "backend/.env" ]; then
    LLM_PROVIDER=$(grep -E "^LLM_PROVIDER=" backend/.env | cut -d '=' -f2)
else
    LLM_PROVIDER="ollama"
fi

# Ollama 사용 시에만 Ollama 서버 실행
OLLAMA_PID=""
if [ "$LLM_PROVIDER" = "ollama" ]; then
    if ! lsof -i :11434 | grep -q LISTEN; then
        echo "Ollama 서버 시작 중..."
        ollama serve > /dev/null 2>&1 &
        OLLAMA_PID=$!
        sleep 2
    else
        echo "Ollama 이미 실행 중"
    fi
else
    echo "LLM Provider: $LLM_PROVIDER"
fi

# 백엔드 실행 (가상환경 활성화 후 uvicorn 직접 실행)
echo "백엔드 서버 시작 중..."
(cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) > backend.log 2>&1 &
BACKEND_PID=$!

# 백엔드가 실제로 시작될 때까지 대기 (최대 30초)
echo "백엔드 서버 시작 대기 중..."
COUNTER=0
while [ $COUNTER -lt 30 ]; do
    if lsof -i :8000 | grep -q LISTEN; then
        echo "백엔드 서버 시작 완료!"
        break
    fi
    sleep 1
    COUNTER=$((COUNTER + 1))
done

if [ $COUNTER -eq 30 ]; then
    echo "백엔드 서버 시작 실패! 로그를 확인하세요:"
    tail -n 20 backend.log
    kill $BACKEND_PID 2>/dev/null
    if [ -n "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null
    fi
    exit 1
fi

# 프론트엔드 실행
echo "프론트엔드 서버 시작 중..."
(cd frontend && npm run dev) > frontend.log 2>&1 &
FRONTEND_PID=$!

# 프론트엔드 시작 대기
sleep 3

echo ""
echo "========================================="
echo "모든 서버가 실행 중입니다!"
echo "백엔드 API: http://localhost:8000"
echo "API 문서: http://localhost:8000/docs"
echo "프론트엔드: http://localhost:3000"
echo ""
echo "로그 파일:"
echo "   - 백엔드: backend.log"
echo "   - 프론트엔드: frontend.log"
echo "========================================="
echo ""

# 브라우저 자동 열기 (2초 후)
sleep 2
echo "브라우저를 열고 있습니다..."
open http://localhost:3000

echo ""
echo "종료하려면 Ctrl+C를 누르세요..."
echo ""
echo "백엔드 로그 (실시간):"
tail -f backend.log &
TAIL_PID=$!

cleanup() {
    echo ""
    echo "서버 종료 중..."
    kill $TAIL_PID 2>/dev/null
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    if [ -n "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null
    fi
    pkill -P $BACKEND_PID 2>/dev/null || true
    pkill -P $FRONTEND_PID 2>/dev/null || true
    echo "모든 서버가 종료되었습니다."
    exit 0
}

trap cleanup SIGINT SIGTERM

wait
