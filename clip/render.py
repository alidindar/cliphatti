"""M2: verilen start/end aralığını 1080x1920, altyazılı MP4'e çevirir.

Kadraj modları:
  crop  ortadan 9:16 kesit (yüz takibi M3'te gelecek)
  blur  videonun tamamı ortada, arkası bulanık büyütülmüş kopya (konuşmacı yoksa)
"""

import json
import subprocess
from pathlib import Path

from clip.captions import HEIGHT, WIDTH, build_ass, clip_words
from clip.transcribe import WORK, video_id

FILTERS = {
    "crop": f"scale=-2:{HEIGHT},crop={WIDTH}:{HEIGHT}",
    "blur": (
        f"split[bg][fg];"
        f"[bg]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},boxblur=24:2[bg];"
        f"[fg]scale={WIDTH}:-2[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
    ),
}


def render(video: Path, start: float, end: float, out: Path | None = None,
           mode: str = "crop", hook: str | None = None) -> Path:
    video = Path(video).resolve()
    if end <= start:
        raise ValueError("end, start'tan büyük olmalı")
    if mode not in FILTERS:
        raise ValueError(f"mode: {', '.join(FILTERS)}")

    work = WORK / video_id(video)
    transcript = work / "transcript.json"
    if not transcript.is_file():
        raise FileNotFoundError(f"önce transkript: python cli.py transcribe {video}")
    data = json.loads(transcript.read_text(encoding="utf-8"))

    name = f"clip_{start:.0f}_{end:.0f}"
    ass = build_ass(clip_words(data["segments"], start, end), work / f"{name}.ass",
                    lang=data["language"], hook=hook)
    out = Path(out).resolve() if out else work / f"{name}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    # subtitles filtresi Windows yollarındaki ':' ve '\' ile sorun çıkarıyor;
    # ffmpeg'i work klasöründe çalıştırıp ASS'e yalnızca dosya adıyla başvuruyoruz.
    vf = f"{FILTERS[mode]},subtitles={ass.name}"
    cmd = [
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start:.3f}", "-i", str(video), "-t", f"{end - start:.3f}",
        "-filter_complex", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True, cwd=work)
    print(f"Klip: {out}")
    return out
