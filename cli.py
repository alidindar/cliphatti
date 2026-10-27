"""ClipHattı komut satırı.

    python cli.py transcribe <video> [--model small] [--lang tr]
    python cli.py render <video> --start 12.5 --end 41 [--mode crop|blur] [--hook "..."]
"""

import argparse
import sys
from pathlib import Path

from clip.render import FILTERS, render
from clip.transcribe import transcribe


def main() -> None:
    # Windows konsolunda Türkçe karakterler bozulmasın.
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(prog="cliphatti")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("transcribe", help="videoyu kelime zamanlı transkripte çevir (M1)")
    p.add_argument("video", type=Path)
    p.add_argument("--model", default="small", help="tiny / base / small / medium / large-v3")
    p.add_argument("--lang", default=None, help="tr, en ... (boşsa otomatik algılanır)")

    p = sub.add_parser("render", help="aralığı 9:16 altyazılı klibe çevir (M2)")
    p.add_argument("video", type=Path)
    p.add_argument("--start", type=float, required=True, help="saniye")
    p.add_argument("--end", type=float, required=True, help="saniye")
    p.add_argument("--mode", default="crop", choices=list(FILTERS))
    p.add_argument("--hook", default=None, help="ilk 2 sn üstte görünecek kanca yazısı")
    p.add_argument("--out", type=Path, default=None)

    args = parser.parse_args()
    if args.cmd == "transcribe":
        transcribe(args.video, model_size=args.model, language=args.lang)
    elif args.cmd == "render":
        render(args.video, args.start, args.end, out=args.out, mode=args.mode, hook=args.hook)


if __name__ == "__main__":
    main()
