"""
Chatterbox TTS API 테스트 클라이언트
다양한 엔드포인트를 테스트하는 예제 스크립트
"""

import requests
import json
from pathlib import Path

# API 서버 URL
BASE_URL = "http://localhost:8000"

def test_health():
    """헬스 체크 테스트"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()

def test_models():
    """모델 목록 조회 테스트"""
    print("Testing /models endpoint...")
    response = requests.get(f"{BASE_URL}/models")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()

def test_tts_turbo(output_dir="outputs"):
    """Turbo 모델 TTS 생성 테스트"""
    print("Testing /tts/turbo endpoint...")

    Path(output_dir).mkdir(exist_ok=True)

    # 병행언어학적 태그 포함
    text = "Hello! [chuckle] This is a test of the Turbo model with paralinguistic tags."

    response = requests.post(
        f"{BASE_URL}/tts/turbo",
        data={"text": text}
    )

    if response.status_code == 200:
        output_path = Path(output_dir) / "turbo_test.wav"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✓ Audio saved to {output_path}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
    print()

def test_tts_multilingual(output_dir="outputs"):
    """Multilingual 모델 TTS 생성 테스트"""
    print("Testing /tts/multilingual endpoint...")

    Path(output_dir).mkdir(exist_ok=True)

    # 여러 언어 테스트
    tests = [
        ("안녕하세요! Chatterbox 다국어 TTS 테스트입니다.", "ko", "korean_test.wav"),
        ("Hello! This is a multilingual TTS test.", "en", "english_test.wav"),
        ("こんにちは！これはマルチリンガルTTSテストです。", "ja", "japanese_test.wav"),
        ("你好！这是多语言TTS测试。", "zh", "chinese_test.wav"),
    ]

    for text, lang_id, filename in tests:
        print(f"  Testing {lang_id}: {text[:50]}...")
        response = requests.post(
            f"{BASE_URL}/tts/multilingual",
            data={
                "text": text,
                "language_id": lang_id
            }
        )

        if response.status_code == 200:
            output_path = Path(output_dir) / filename
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"  ✓ Audio saved to {output_path}")
        else:
            print(f"  ✗ Error: {response.status_code}")
            print(f"  {response.text}")

    print()

def test_tts_json(output_dir="outputs"):
    """JSON 형식으로 TTS 생성 테스트"""
    print("Testing /tts endpoint with JSON...")

    Path(output_dir).mkdir(exist_ok=True)

    request_data = {
        "text": "This is a test using the JSON API endpoint.",
        "model_type": "turbo"
    }

    response = requests.post(
        f"{BASE_URL}/tts",
        json=request_data
    )

    if response.status_code == 200:
        output_path = Path(output_dir) / "json_api_test.wav"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✓ Audio saved to {output_path}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
    print()

def test_tts_with_voice(voice_file_path=None, output_dir="outputs"):
    """커스텀 음성으로 TTS 생성 테스트"""
    print("Testing /tts/with-voice endpoint...")

    if not voice_file_path:
        print("⚠ No voice file provided. Skipping this test.")
        print("  Usage: Provide a voice file path as argument")
        print()
        return

    voice_path = Path(voice_file_path)
    if not voice_path.exists():
        print(f"✗ Voice file not found: {voice_file_path}")
        print()
        return

    Path(output_dir).mkdir(exist_ok=True)

    text = "This audio will be generated using the reference voice you provided."

    with open(voice_path, "rb") as voice_file:
        response = requests.post(
            f"{BASE_URL}/tts/with-voice",
            data={
                "text": text,
                "model_type": "turbo"
            },
            files={"voice_file": voice_file}
        )

    if response.status_code == 200:
        output_path = Path(output_dir) / "custom_voice_test.wav"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✓ Audio with custom voice saved to {output_path}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
    print()

def test_error_handling():
    """에러 처리 테스트"""
    print("Testing error handling...")

    # 너무 긴 텍스트
    print("  Testing text length validation...")
    long_text = "A" * 10000
    response = requests.post(
        f"{BASE_URL}/tts/turbo",
        data={"text": long_text}
    )
    if response.status_code == 400:
        print(f"  ✓ Text length validation working: {response.status_code}")
    else:
        print(f"  ✗ Unexpected response: {response.status_code}")

    # 잘못된 모델 타입
    print("  Testing invalid model type...")
    response = requests.post(
        f"{BASE_URL}/tts",
        json={
            "text": "Test",
            "model_type": "invalid_model"
        }
    )
    if response.status_code == 422:  # Validation error
        print(f"  ✓ Model validation working: {response.status_code}")
    else:
        print(f"  ✗ Unexpected response: {response.status_code}")

    print()

def main():
    """모든 테스트 실행"""
    print("=" * 60)
    print("Chatterbox TTS API Test Client")
    print("=" * 60)
    print()

    try:
        # 기본 정보 테스트
        test_health()
        test_models()

        # TTS 생성 테스트
        test_tts_json()
        test_tts_turbo()
        test_tts_multilingual()

        # 커스텀 음성 테스트 (음성 파일이 있는 경우)
        # test_tts_with_voice("path/to/your/voice.wav")

        # 에러 처리 테스트
        test_error_handling()

        print("=" * 60)
        print("All tests completed!")
        print("Check the 'outputs' directory for generated audio files.")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API server.")
        print(f"  Make sure the server is running at {BASE_URL}")
        print("  Run: python api_server.py")

if __name__ == "__main__":
    main()
