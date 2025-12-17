#!/bin/bash
# Chatterbox TTS API 서버 시작 스크립트

echo "Starting Chatterbox TTS API Server..."

# 환경 변수 설정 (필요한 경우)
export PYTHONPATH="${PYTHONPATH}:$(dirname $(pwd))/src"

# 기본 설정
HOST="${CHATTERBOX_HOST:-0.0.0.0}"
PORT="${CHATTERBOX_PORT:-8000}"
WORKERS="${WORKERS:-1}"

# 개발/프로덕션 모드 선택
if [ "$1" = "dev" ]; then
    echo "Running in development mode with auto-reload..."
    uvicorn api_server:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload
else
    echo "Running in production mode..."
    uvicorn api_server:app \
        --host "$HOST" \
        --port "$PORT" \
        --workers "$WORKERS"
fi
