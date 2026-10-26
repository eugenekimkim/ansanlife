#!/usr/bin/env python3
"""안산살이 모바일웹 빌드 스크립트.

src/app.template.html 을 읽어 실행 가능한 HTML 을 만듭니다.

  python3 build.py                 # index.html 생성 (이미지는 assets/ 파일 참조)
  NAVER_KEY=xxxx python3 build.py  # 네이버 지도 Client ID(ncpKeyId)를 넣어 빌드
  python3 build.py --inline        # 이미지를 base64로 넣은 단일 파일 dist/ansanlife-inline.html 생성
                                   # (Claude 아티팩트처럼 파일 하나만 올릴 때)
"""
import base64
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "src" / "app.template.html"

HEAD = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
"""
TAIL = "\n</body></html>\n"


def data_uri(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def main() -> None:
    inline = "--inline" in sys.argv
    key = os.environ.get("NAVER_KEY", "").strip()
    html = TEMPLATE.read_text(encoding="utf-8")

    orange = ROOT / "assets" / "intro-orange.jpg"
    sky = ROOT / "assets" / "intro-sky.jpg"
    if inline:
        html = html.replace("__ORANGE__", data_uri(orange)).replace("__SKY__", data_uri(sky))
    else:
        html = html.replace("__ORANGE__", "assets/intro-orange.jpg").replace("__SKY__", "assets/intro-sky.jpg")

    # 키가 비어 있으면 앱은 그림 지도로 대신 보여줍니다.
    html = html.replace("const NAVER_KEY='__NAVER_KEY__';", f"const NAVER_KEY='{key}';")

    if inline:
        out = ROOT / "dist" / "ansanlife-inline.html"
        out.parent.mkdir(exist_ok=True)
    else:
        out = ROOT / "index.html"
    out.write_text(HEAD + html + TAIL, encoding="utf-8")
    print(f"built {out.relative_to(ROOT)}  (naver map: {'on' if key else 'off'})")


if __name__ == "__main__":
    main()
