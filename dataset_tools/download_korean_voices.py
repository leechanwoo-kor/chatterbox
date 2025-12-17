"""
Hugging Face 데이터셋에서 한국어 음성 파일만 다운로드하는 스크립트
Dataset: https://huggingface.co/datasets/simon3000/genshin-voice

스트리밍 모드를 사용하여 디스크 공간을 절약합니다.
"""

from datasets import load_dataset, Features, Value, Audio
from pathlib import Path
import os
from tqdm import tqdm
import requests
import io

def download_korean_voices(output_dir="data/korean_voices", max_samples=None):
    """
    Genshin Voice 데이터셋에서 한국어 음성만 다운로드 (스트리밍 모드)

    Args:
        output_dir: 저장할 디렉토리 경로
        max_samples: 최대 다운로드 샘플 수 (None이면 모두 다운로드)
    """
    print("=" * 60)
    print("Genshin Voice Dataset - Korean Voice Downloader")
    print("(Using streaming mode to save disk space)")
    print("=" * 60)
    print()

    # 출력 디렉토리 생성
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_path.absolute()}")
    if max_samples:
        print(f"Max samples: {max_samples}")
    print()

    try:
        import soundfile as sf
        import numpy as np

        # 스트리밍 모드로 데이터셋 로드 (오디오 디코딩 비활성화)
        print("Loading dataset in streaming mode...")
        print("(This doesn't download the entire dataset)")
        print()

        # 오디오 컬럼을 일반 딕셔너리로 처리하도록 설정
        dataset = load_dataset(
            "simon3000/genshin-voice",
            split="train",
            streaming=True
        )

        # 오디오를 bytes로 가져오도록 설정 (자동 디코딩 비활성화)
        dataset = dataset.cast_column("audio", Audio(decode=False))

        print(f"✓ Dataset loaded successfully (streaming mode)")
        print()

        # 메타데이터 파일 생성
        metadata_file = output_path / "metadata.txt"

        # 음성 파일 다운로드 (스트리밍)
        print("Processing Korean voices only...")
        print("(Only Korean audio files will be downloaded)")
        print()

        korean_count = 0
        total_processed = 0

        with open(metadata_file, "w", encoding="utf-8") as meta_f:
            # 헤더 작성
            meta_f.write("filename|speaker|transcription|language|speaker_type\n")

            # 스트리밍 데이터셋을 순회하며 한국어만 필터링
            with tqdm(desc="Processing", unit=" samples") as pbar:
                for sample in dataset:
                    total_processed += 1
                    pbar.update(1)

                    # 한국어 체크
                    if sample.get('language') != 'Korean':
                        continue

                    try:
                        # 파일명 생성 (speaker_idx.wav)
                        speaker = sample.get('speaker', 'unknown')
                        # 파일명에 안전한 문자만 사용
                        safe_speaker = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in speaker)
                        filename = f"{safe_speaker}_{korean_count:04d}.wav"
                        file_path = output_path / filename

                        # 오디오 데이터 가져오기 (bytes 형태)
                        audio_data = sample['audio']

                        # bytes에서 오디오 로드
                        if 'bytes' in audio_data:
                            audio_bytes = audio_data['bytes']
                        elif 'path' in audio_data:
                            # 파일 경로에서 읽기
                            with open(audio_data['path'], 'rb') as f:
                                audio_bytes = f.read()
                        else:
                            raise ValueError("Audio data format not supported")

                        # soundfile로 오디오 읽기
                        audio_array, sample_rate = sf.read(io.BytesIO(audio_bytes))

                        # WAV 파일로 저장
                        sf.write(file_path, audio_array, sample_rate)

                        # 메타데이터 저장
                        text = sample.get('transcription', '').replace('|', ' ')
                        language = sample.get('language', 'Korean')
                        speaker_type = sample.get('speaker_type', '')
                        meta_f.write(f"{filename}|{speaker}|{text}|{language}|{speaker_type}\n")

                        korean_count += 1
                        pbar.set_postfix({"Korean": korean_count})

                        # 최대 샘플 수 체크
                        if max_samples and korean_count >= max_samples:
                            print(f"\n✓ Reached max samples limit: {max_samples}")
                            break

                    except Exception as e:
                        print(f"\n  ✗ Error processing Korean sample {korean_count}: {e}")
                        continue

        print()
        print("=" * 60)
        print("Download completed!")
        print("=" * 60)
        print(f"✓ Downloaded {korean_count} Korean voice files")
        print(f"✓ Total processed: {total_processed} samples")
        print(f"✓ Files saved to: {output_path.absolute()}")
        print(f"✓ Metadata saved to: {metadata_file.absolute()}")
        print()

        # 화자별 통계 (메타데이터 파일에서 읽기)
        speakers = {}
        with open(metadata_file, "r", encoding="utf-8") as f:
            next(f)  # 헤더 스킵
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    speaker = parts[1]
                    speakers[speaker] = speakers.get(speaker, 0) + 1

        if speakers:
            print("Speaker statistics:")
            for speaker, count in sorted(speakers.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  - {speaker}: {count} samples")
            if len(speakers) > 10:
                print(f"  ... and {len(speakers) - 10} more speakers")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def list_available_languages(max_check=1000):
    """데이터셋의 사용 가능한 언어 목록 확인 (스트리밍 모드)"""
    print(f"Checking available languages in dataset (first {max_check} samples)...")
    print()

    try:
        # 스트리밍 모드로 데이터셋 로드 (오디오 디코딩 비활성화)
        dataset = load_dataset(
            "simon3000/genshin-voice",
            split="train",
            streaming=True
        )

        # 오디오를 디코딩하지 않도록 설정
        dataset = dataset.cast_column("audio", Audio(decode=False))

        # 언어별 통계
        languages = {}
        count = 0

        with tqdm(total=max_check, desc="Checking") as pbar:
            for sample in dataset:
                lang = sample.get('language', 'unknown')
                languages[lang] = languages.get(lang, 0) + 1
                count += 1
                pbar.update(1)

                if count >= max_check:
                    break

        print("\nAvailable languages:")
        for lang, sample_count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            percentage = (sample_count / count) * 100
            print(f"  - {lang}: {sample_count} samples ({percentage:.1f}%)")

        print(f"\nNote: Checked first {count} samples only")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Download Korean voices from Genshin Voice dataset (streaming mode)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/korean_voices",
        help="Output directory for downloaded files (default: data/korean_voices)"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Maximum number of Korean samples to download (default: all)"
    )
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List available languages in the dataset"
    )
    parser.add_argument(
        "--check-samples",
        type=int,
        default=1000,
        help="Number of samples to check when listing languages (default: 1000)"
    )

    args = parser.parse_args()

    if args.list_languages:
        list_available_languages(args.check_samples)
    else:
        download_korean_voices(args.output_dir, args.max_samples)
