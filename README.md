# ClipHattı

Uzun bir videodan dikey (9:16), kelime kelime altyazılı kısa klip üreten komut satırı aracı.

- `transcribe`: faster-whisper ile kelime düzeyinde zaman damgalı transkript çıkarır (`work/<video>/transcript.json`). Ses ffmpeg ile 16 kHz mono'ya çevrilir.
- `render`: seçilen aralığı 1080x1920 MP4'e çevirir. ASS altyazıda o an söylenen kelime vurgulanır; ilk 2 saniyede isteğe bağlı bir kanca yazısı gösterilir. Kadraj modları: `crop` (ortadan kesit) ve `blur` (bulanık arka plan üstünde videonun tamamı).

## Kurulum

ffmpeg PATH'te olmalı.

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## Kullanım

```
python cli.py transcribe video.mp4 --model small --lang tr
python cli.py render video.mp4 --start 12.5 --end 41 --mode crop --hook "Kanca yazısı"
```
