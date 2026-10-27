"""ClipHattı komut satırı.

    python cli.py transcribe <video> [--model small] [--lang tr]
"""

import argparse
import sys
from pathlib import Path

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

    args = parser.parse_args()
    if args.cmd == "transcribe":
        transcribe(args.video, model_size=args.model, language=args.lang)


if __name__ == "__main__":
    main()
