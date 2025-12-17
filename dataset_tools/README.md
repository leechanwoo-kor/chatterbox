# Dataset Tools

Hugging Face에서 음성 데이터셋을 다운로드하는 도구 모음입니다.

## 설치

```bash
cd dataset_tools

# 의존성 설치
pip install -r requirements.txt
```

## Genshin Voice Dataset - 한국어 음성 다운로드

원본 데이터셋: https://huggingface.co/datasets/simon3000/genshin-voice

⚠️ **중요**: 이 스크립트는 **스트리밍 모드**를 사용하여 한국어 음성만 다운로드합니다.
전체 데이터셋(200GB+)을 다운로드하지 않으므로 디스크 공간을 절약할 수 있습니다.

### 기본 사용법

```bash
# 한국어 음성만 다운로드 (기본 경로: data/korean_voices)
python download_korean_voices.py

# 커스텀 출력 경로 지정
python download_korean_voices.py --output-dir ../data/my_korean_voices

# 최대 100개 샘플만 다운로드 (테스트용)
python download_korean_voices.py --max-samples 100

# 데이터셋의 사용 가능한 언어 목록 확인 (첫 1000개 샘플 체크)
python download_korean_voices.py --list-languages

# 언어 확인 시 더 많은 샘플 체크
python download_korean_voices.py --list-languages --check-samples 5000
```

### 출력 파일 구조

다운로드 후 다음과 같은 구조로 파일이 생성됩니다:

```
data/korean_voices/
├── metadata.txt              # 메타데이터 (파일명|캐릭터|텍스트|언어)
├── character_0000.wav        # 음성 파일 1
├── character_0001.wav        # 음성 파일 2
├── character_0002.wav        # 음성 파일 3
└── ...
```

### metadata.txt 형식

```
filename|character|text|language
character_0000.wav|Paimon|안녕하세요!|Korean
character_0001.wav|Traveler|좋은 아침입니다.|Korean
...
```

## 다운로드한 음성으로 TTS 테스트

다운로드한 음성 파일을 Chatterbox TTS API의 참조 음성으로 사용할 수 있습니다:

```bash
# API 서버가 실행 중일 때
curl -X POST "http://localhost:8000/tts/with-voice" \
  -F "text=이것은 커스텀 음성 테스트입니다." \
  -F "model_type=multilingual" \
  -F "language_id=ko" \
  -F "voice_file=@../data/korean_voices/character_0000.wav" \
  --output custom_korean_voice.wav
```

또는 Python으로:

```python
import requests

voice_file_path = "../data/korean_voices/character_0000.wav"

with open(voice_file_path, "rb") as voice_file:
    response = requests.post(
        "http://localhost:8000/tts/with-voice",
        data={
            "text": "이것은 커스텀 음성 테스트입니다.",
            "model_type": "multilingual",
            "language_id": "ko"
        },
        files={"voice_file": voice_file}
    )

with open("custom_korean_voice.wav", "wb") as f:
    f.write(response.content)
```

## 추가 기능

### 캐릭터별 통계

스크립트는 다운로드 완료 후 캐릭터별 음성 파일 개수를 자동으로 표시합니다:

```
Character statistics:
  - Paimon: 1234 samples
  - Traveler: 567 samples
  - Amber: 345 samples
  ...
```

### 에러 처리

- 개별 파일 다운로드 실패 시 해당 파일을 건너뛰고 계속 진행
- 진행 상황을 tqdm 프로그레스 바로 표시
- 모든 에러는 콘솔에 출력

## 참고사항

- 첫 실행 시 Hugging Face에서 데이터셋을 다운로드하므로 시간이 걸릴 수 있습니다
- 데이터셋은 `~/.cache/huggingface/` 에 캐시됩니다
- 음성 파일은 WAV 형식으로 저장됩니다
- 한국어 외 다른 언어도 필터링 가능 (스크립트 수정 필요)

## 라이선스

이 도구는 Chatterbox 프로젝트의 일부입니다.
데이터셋의 라이선스는 원본 데이터셋 페이지를 참조하세요.
