"""Kelime kelime ASS altyazı: büyük harf, ortalı, o an söylenen kelime vurgulu.

Zamanlar klibin başına göredir (0 = klip başlangıcı).
"""

from pathlib import Path

WIDTH, HEIGHT = 1080, 1920
MAX_WORDS = 3     # ekranda aynı anda en fazla kaç kelime
MAX_GAP = 0.6     # kelimeler arası bu kadar sessizlik olursa yeni grup
HOOK_SECONDS = 2.0

# ASS renkleri &HAABBGGRR biçiminde
WHITE = "&H00FFFFFF"
YELLOW = "&H0000E5FF"

HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,Arial,96,{WHITE},{WHITE},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,3,2,60,60,560,1
Style: Hook,Arial,78,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,18,0,8,80,80,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _ts(sec: float) -> str:
    sec = max(0.0, sec)
    cs = int(round(sec * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _upper(text: str, lang: str | None) -> str:
    # str.upper() Türkçede i -> I yapar; doğrusu i -> İ, ı -> I.
    if lang == "tr":
        text = text.replace("i", "İ").replace("ı", "I")
    return text.upper()


def _clean(text: str) -> str:
    # ASS'de { } \ özel anlamlı.
    return text.replace("\\", "").replace("{", "(").replace("}", ")")


def clip_words(segments: list, start: float, end: float) -> list:
    """Klip aralığına düşen kelimeleri klibe göre kaydırılmış zamanlarla döndürür."""
    words = []
    for seg in segments:
        for w in seg["words"]:
            if w["end"] <= start or w["start"] >= end or not w["word"]:
                continue
            words.append({
                "start": max(w["start"], start) - start,
                "end": min(w["end"], end) - start,
                "word": w["word"],
            })
    return words


def _groups(words: list) -> list:
    groups, cur = [], []
    for w in words:
        if cur and (len(cur) >= MAX_WORDS or w["start"] - cur[-1]["end"] > MAX_GAP):
            groups.append(cur)
            cur = []
        cur.append(w)
        if w["word"][-1] in ".?!,;:":
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def build_ass(words: list, out_path: Path, lang: str | None = None, hook: str | None = None) -> Path:
    lines = [HEADER]

    if hook:
        lines.append(f"Dialogue: 1,{_ts(0)},{_ts(HOOK_SECONDS)},Hook,,0,0,0,,{_clean(_upper(hook, lang))}\n")

    for group in _groups(words):
        texts = [_clean(_upper(w["word"], lang)) for w in group]
        for i, w in enumerate(group):
            # Bir sonraki kelime başlayana kadar ekranda kalsın, grup arasında titreme olmasın.
            stop = group[i + 1]["start"] if i + 1 < len(group) else w["end"]
            if stop <= w["start"]:
                stop = w["start"] + 0.05
            parts = [
                f"{{\\c{YELLOW}}}{t}{{\\c{WHITE}}}" if j == i else t
                for j, t in enumerate(texts)
            ]
            lines.append(f"Dialogue: 0,{_ts(w['start'])},{_ts(stop)},Word,,0,0,0,,{' '.join(parts)}\n")

    out_path.write_text("".join(lines), encoding="utf-8")
    return out_path
