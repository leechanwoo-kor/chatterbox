# Chatterbox TTS API Server

FastAPI 기반의 Chatterbox Text-to-Speech REST API 서버입니다.

## 특징

- 🚀 **3가지 모델 지원**: Turbo, Multilingual, Original
- 🌍 **다국어 지원**: 23개 이상의 언어 (한국어, 영어, 일본어, 중국어 등)
- 🎭 **음성 복제**: 커스텀 음성 파일을 업로드하여 음성 복제
- ⚡ **병행언어학적 태그**: `[laugh]`, `[cough]`, `[chuckle]` 등의 감정 표현
- 🐳 **Docker 지원**: Docker 및 Docker Compose로 간편한 배포
- 📝 **자동 문서화**: Swagger UI 및 ReDoc 제공

## 빠른 시작

### 1. Conda 가상환경 설정 (권장)

```bash
# Conda 가상환경 생성 (Python 3.11)
conda create -n chatterbox-api python=3.11 -y

# 가상환경 활성화
conda activate chatterbox-api

# API 디렉토리로 이동
cd api

# 의존성 설치
pip install -r requirements-api.txt

# 루트 디렉토리에서 chatterbox 패키지 설치
cd ..
pip install -e .
cd api
```

### 1-1. 일반 pip 설치 (대안)

```bash
# API 디렉토리로 이동
cd api

# 의존성 설치
pip install -r requirements-api.txt

# 또는 루트 디렉토리에서 chatterbox 설치
cd ..
pip install -e .
cd api
pip install fastapi uvicorn python-multipart pydantic pydantic-settings
```

### 2. 서버 실행

```bash
# Windows
start.bat dev

# Linux/Mac
./start.sh dev

# 또는 직접 실행
python api_server.py

# 또는 uvicorn 직접 실행
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

### 3. API 문서 확인

서버 실행 후 브라우저에서 다음 주소로 접속:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 사용 예제

### 기본 TTS 생성 (JSON)

```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "안녕하세요, Chatterbox TTS API 테스트입니다.",
    "model_type": "turbo"
  }' \
  --output output.wav
```

### Turbo 모델 (Form Data)

```bash
curl -X POST "http://localhost:8000/tts/turbo" \
  -F "text=Hello! [chuckle] This is a test with paralinguistic tags." \
  --output turbo_output.wav
```

### Multilingual 모델 (한국어)

```bash
curl -X POST "http://localhost:8000/tts/multilingual" \
  -F "text=안녕하세요, 반갑습니다!" \
  -F "language_id=ko" \
  --output korean_output.wav
```

### 커스텀 음성으로 생성

```bash
curl -X POST "http://localhost:8000/tts/with-voice" \
  -F "text=This will sound like the reference voice." \
  -F "model_type=turbo" \
  -F "voice_file=@your_voice_sample.wav" \
  --output custom_voice_output.wav
```

### Python 클라이언트 예제

```python
import requests

# 기본 TTS 생성
response = requests.post(
    "http://localhost:8000/tts",
    json={
        "text": "안녕하세요, 반갑습니다!",
        "model_type": "multilingual",
        "language_id": "ko"
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)

# 커스텀 음성 사용
with open("reference_voice.wav", "rb") as voice_file:
    response = requests.post(
        "http://localhost:8000/tts/with-voice",
        data={
            "text": "Custom voice test",
            "model_type": "turbo"
        },
        files={"voice_file": voice_file}
    )

with open("custom_output.wav", "wb") as f:
    f.write(response.content)
```

### JavaScript/TypeScript 예제

```typescript
// 기본 TTS 생성
async function generateTTS(text: string, modelType: string = "turbo") {
  const response = await fetch("http://localhost:8000/tts", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text: text,
      model_type: modelType,
    }),
  });

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);

  // 오디오 재생
  const audio = new Audio(url);
  audio.play();
}

// 사용 예
generateTTS("안녕하세요!", "multilingual");

// 커스텀 음성 사용
async function generateWithCustomVoice(text: string, voiceFile: File) {
  const formData = new FormData();
  formData.append("text", text);
  formData.append("model_type", "turbo");
  formData.append("voice_file", voiceFile);

  const response = await fetch("http://localhost:8000/tts/with-voice", {
    method: "POST",
    body: formData,
  });

  const blob = await response.blob();
  return URL.createObjectURL(blob);
}
```

## API 엔드포인트

### GET `/`
API 정보 및 사용 가능한 엔드포인트 목록

### GET `/health`
서버 상태 및 로드된 모델 확인

**응답 예시:**
```json
{
  "status": "healthy",
  "device": "cuda",
  "loaded_models": ["turbo"]
}
```

### GET `/models`
사용 가능한 모델 목록 및 기능

### POST `/tts`
범용 TTS 생성 엔드포인트

**요청 본문 (JSON):**
```json
{
  "text": "변환할 텍스트",
  "model_type": "turbo|multilingual|original",
  "language_id": "ko" // multilingual 모델에서만 사용
}
```

### POST `/tts/turbo`
Turbo 모델 전용 엔드포인트

**Form Data:**
- `text`: 변환할 텍스트 (paralinguistic tags 지원)

### POST `/tts/multilingual`
Multilingual 모델 전용 엔드포인트

**Form Data:**
- `text`: 변환할 텍스트
- `language_id`: 언어 코드 (ko, en, ja, zh 등)

### POST `/tts/original`
Original 모델 전용 엔드포인트

**Form Data:**
- `text`: 변환할 텍스트

### POST `/tts/with-voice`
커스텀 음성 참조를 사용한 TTS 생성

**Form Data:**
- `text`: 변환할 텍스트
- `model_type`: 사용할 모델 (turbo, multilingual, original)
- `language_id`: (선택) 언어 코드
- `voice_file`: 참조 음성 파일 (WAV 권장)

## 환경 설정

`.env` 파일을 생성하여 설정을 커스터마이즈할 수 있습니다:

```bash
# .env.example을 복사
cp .env.example .env
```

**주요 설정 항목:**

```env
# 서버 설정
CHATTERBOX_HOST=0.0.0.0
CHATTERBOX_PORT=8000

# 모델 설정
CHATTERBOX_DEFAULT_MODEL=turbo
CHATTERBOX_PRELOAD_MODELS=  # 시작 시 미리 로드할 모델 (쉼표로 구분)

# 디바이스 설정 (자동 감지하려면 비워두기)
CHATTERBOX_DEVICE=  # cuda, mps, cpu 중 하나

# 오디오 설정
CHATTERBOX_MAX_TEXT_LENGTH=5000
CHATTERBOX_OUTPUT_FORMAT=wav
```

## Docker로 실행

### Docker Compose 사용 (권장)

```bash
cd api
docker-compose up -d
```

### Docker 직접 사용

```bash
# 이미지 빌드
docker build -t chatterbox-api -f api/Dockerfile .

# 컨테이너 실행 (GPU 사용)
docker run --gpus all -p 8000:8000 chatterbox-api

# 컨테이너 실행 (CPU만 사용)
docker run -p 8000:8000 chatterbox-api
```

## 지원 언어 목록

Multilingual 모델은 다음 언어를 지원합니다:

| 언어 | 코드 | 언어 | 코드 | 언어 | 코드 |
|------|------|------|------|------|------|
| 아랍어 | ar | 덴마크어 | da | 독일어 | de |
| 그리스어 | el | 영어 | en | 스페인어 | es |
| 핀란드어 | fi | 프랑스어 | fr | 히브리어 | he |
| 힌디어 | hi | 이탈리아어 | it | 일본어 | ja |
| 한국어 | ko | 말레이어 | ms | 네덜란드어 | nl |
| 노르웨이어 | no | 폴란드어 | pl | 포르투갈어 | pt |
| 러시아어 | ru | 스웨덴어 | sv | 스와힐리어 | sw |
| 터키어 | tr | 중국어 | zh | | |

## 병행언어학적 태그 (Turbo 모델)

Turbo 모델은 다음과 같은 감정 표현 태그를 지원합니다:

- `[laugh]` - 웃음
- `[chuckle]` - 낄낄거림
- `[cough]` - 기침
- 그 외 다양한 태그들

**사용 예시:**
```
"Hi there! [chuckle] How are you doing today?"
"I'm sorry to hear that. [cough] Let me help you with that."
```

## 성능 최적화

### GPU 사용
CUDA를 지원하는 GPU가 있다면 자동으로 GPU를 사용합니다. `.env` 파일에서 `CHATTERBOX_DEVICE=cuda`로 설정할 수 있습니다.

### 모델 사전 로드
자주 사용하는 모델을 서버 시작 시 미리 로드하려면:

```env
CHATTERBOX_PRELOAD_MODELS=turbo,multilingual
```

### 메모리 관리
- Turbo 모델: 약 350M 파라미터 (~1.5GB VRAM)
- Multilingual/Original 모델: 약 500M 파라미터 (~2GB VRAM)

## 문제 해결

### 모델 다운로드 문제
첫 실행 시 모델이 자동으로 다운로드됩니다. 인터넷 연결을 확인하세요.

### CUDA Out of Memory
GPU 메모리가 부족한 경우:
- `.env`에서 `CHATTERBOX_DEVICE=cpu` 설정
- 한 번에 하나의 모델만 사용

### 음성 파일 업로드 오류
- WAV 형식 권장
- 파일 크기 제한 확인
- 샘플레이트: 16kHz 이상 권장

## 프로덕션 배포

프로덕션 환경에서는 다음 사항을 고려하세요:

1. **CORS 설정**: `.env`에서 `CHATTERBOX_ALLOW_ORIGINS` 설정
2. **HTTPS 사용**: Nginx 또는 Caddy와 함께 사용
3. **로드 밸런싱**: 여러 인스턴스를 실행하고 로드 밸런서 사용
4. **모니터링**: `/health` 엔드포인트로 헬스 체크

### Nginx 설정 예시

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 라이선스

이 프로젝트는 Chatterbox 오픈소스 프로젝트를 기반으로 합니다.
자세한 내용은 [LICENSE](../LICENSE) 파일을 참조하세요.

## 기여

버그 리포트나 기능 제안은 GitHub Issues를 통해 해주세요.

## 참고 자료

- [Chatterbox 원본 저장소](https://github.com/resemble-ai/chatterbox)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Resemble AI](https://resemble.ai)
