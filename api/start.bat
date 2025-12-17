@echo off
REM Chatterbox TTS API 서버 시작 스크립트 (Windows)

echo Starting Chatterbox TTS API Server...

REM 환경 변수 설정 (필요한 경우)
set PYTHONPATH=%PYTHONPATH%;%~dp0..\src

REM 기본 설정
if "%CHATTERBOX_HOST%"=="" set CHATTERBOX_HOST=0.0.0.0
if "%CHATTERBOX_PORT%"=="" set CHATTERBOX_PORT=8000

REM 개발/프로덕션 모드 선택
if "%1"=="dev" (
    echo Running in development mode with auto-reload...
    uvicorn api_server:app --host %CHATTERBOX_HOST% --port %CHATTERBOX_PORT% --reload
) else (
    echo Running in production mode...
    uvicorn api_server:app --host %CHATTERBOX_HOST% --port %CHATTERBOX_PORT%
)
