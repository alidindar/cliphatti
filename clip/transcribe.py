"""M1: faster-whisper ile kelime düzeyinde zaman damgalı transkript.

Çıktı: work/<video_id>/transcript.json
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work"
SAMPLE_RATE = 16000


def load_audio(video: Path):
    """Sesi ffmpeg ile 16 kHz mono float32 diziye çevirir.

    faster-whisper'ın kendi çözücüsü PyAV'a bağlı ve PyAV 19 ile uyumsuz;
    ffmpeg zaten zorunlu bağımlılık olduğu için onu kullanıyoruz.
    """
    cmd = [
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
        "-i", str(video), "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE),
        "-f", "s16le", "-",
    ]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def video_id(video: Path) -> str:
    """Dosya adından klasör adı olarak güvenli bir kimlik üretir."""
    vid = re.sub(r"[^A-Za-z0-9_-]+", "_", video.stem).strip("_")
    return vid or "video"


def transcribe(video: Path, model_size: str = "small", language: str | None = None) -> Path:
    from faster_whisper import WhisperModel

    video = Path(video).resolve()
    if not video.is_file():
        raise FileNotFoundError(video)

    out_dir = WORK / video_id(video)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "transcript.json"

    print(f"Model yükleniyor: {model_size} (CPU, int8)")
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)

    started = time.time()
    segments, info = model.transcribe(
        load_audio(video),
        language=language,
        word_timestamps=True,
        vad_filter=True,
    )
    print(f"Dil: {info.language} (olasılık {info.language_probability:.2f}), süre {info.duration:.0f} sn")

    result = []
    for seg in segments:
        result.append({
            "id": seg.id,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
            "words": [
                {
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "word": w.word.strip(),
                    "prob": round(w.probability, 3),
                }
                for w in (seg.words or [])
            ],
        })
        pct = min(100.0, seg.end / info.duration * 100) if info.duration else 0.0
        print(f"\r  %{pct:5.1f}  ({seg.end:.0f}/{info.duration:.0f} sn)", end="", flush=True)
    print()

    data = {
        "video": str(video),
        "video_id": video_id(video),
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "duration": round(info.duration, 3),
        "model": model_size,
        "elapsed_sec": round(time.time() - started, 1),
        "segments": result,
    }

    # Yarım kalan bir koşu eski transkripti bozmasın diye önce geçici dosyaya yaz.
    tmp = out_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, out_path)

    words = sum(len(s["words"]) for s in result)
    print(f"Bitti: {len(result)} segment, {words} kelime, {data['elapsed_sec']} sn -> {out_path}")
    return out_path


if __name__ == "__main__":
    transcribe(Path(sys.argv[1]))
