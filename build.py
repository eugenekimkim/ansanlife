#!/usr/bin/env python3
"""안산살이 모바일웹 빌드 스크립트.

src/app.template.html 을 읽어 실행 가능한 HTML 을 만듭니다.

  python3 build.py                 # index.html 생성 (이미지는 assets/ 파일 참조)
  NAVER_KEY=xxxx python3 build.py  # 네이버 지도 Client ID(ncpKeyId)를 넣어 빌드
  GMAPS_KEY=AIza... python3 build.py  # 구글 지도 키 (네이버 키가 없거나 인증 실패일 때 사용)
  API_URL=https://... python3 build.py   # API 서버(사진 분석·버스·공지 번역) 주소를 넣어 빌드 (server/README.md)
  SUPABASE_URL=... SUPABASE_ANON_KEY=... python3 build.py   # 공지·광고·설문 저장 (supabase/README.md)
  ADSENSE_CLIENT=ca-pub-... ADSENSE_SLOT=... python3 build.py  # 직접 광고가 없을 때 애드센스
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
<meta name="theme-color" content="#22393A">
<meta name="description" content="안산 거주 외국인 주민을 위한 다국어 생활 안내 · Life in Ansan for foreign residents">
__PWA__<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
"""
TAIL = "\n</body></html>\n"


def data_uri(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def main() -> None:
    inline = "--inline" in sys.argv
    key = os.environ.get("NAVER_KEY", "").strip()
    analyze = (os.environ.get("API_URL") or os.environ.get("ANALYZE_URL") or "").strip().rstrip("/")
    local = analyze.startswith(("http://localhost", "http://127.0.0.1"))  # 내 컴퓨터에서 wrangler dev 로 시험할 때
    if analyze and not (analyze.startswith("https://") or local):
        sys.exit("API_URL 은 https:// 로 시작해야 합니다 (내 컴퓨터 시험용 http://localhost 는 허용)")
    html = TEMPLATE.read_text(encoding="utf-8")

    orange = ROOT / "assets" / "intro-orange.jpg"
    sky = ROOT / "assets" / "intro-sky.jpg"
    if inline:
        html = html.replace("__ORANGE__", data_uri(orange)).replace("__SKY__", data_uri(sky))
    else:
        html = html.replace("__ORANGE__", "assets/intro-orange.jpg").replace("__SKY__", "assets/intro-sky.jpg")

    # 키가 비어 있으면 앱은 그림 지도로 대신 보여줍니다.
    html = html.replace("const NAVER_KEY='__NAVER_KEY__';", f"const NAVER_KEY='{key}';")
    gkey = os.environ.get("GMAPS_KEY", "").strip()
    html = html.replace("const GMAPS_KEY='__GMAPS_KEY__';", f"const GMAPS_KEY='{gkey}';")
    # 비어 있으면 사진 분석·버스·공지는 예시 데이터로 보여줍니다.
    html = html.replace("'__API_URL__'", f"'{analyze}'")
    # Supabase 공개(anon) 키·애드센스는 원래 공개되는 값이라 빌드에 넣어도 됩니다 (비밀 키는 절대 넣지 마세요)
    sb_url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    sb_key = os.environ.get("SUPABASE_ANON_KEY", "").strip()
    if sb_url and not sb_url.startswith("https://"):
        sys.exit("SUPABASE_URL 은 https:// 로 시작해야 합니다")
    if sb_key.count(".") != 2 and not sb_key.startswith("sb_publishable_") and sb_key:
        sys.exit("SUPABASE_ANON_KEY 는 anon(공개) 키여야 합니다")
    html = html.replace("'__SUPABASE_URL__'", f"'{sb_url}'").replace("'__SUPABASE_ANON_KEY__'", f"'{sb_key}'")
    html = html.replace("'__ADSENSE_CLIENT__'", f"'{os.environ.get('ADSENSE_CLIENT', '').strip()}'")
    html = html.replace("'__ADSENSE_SLOT__'", f"'{os.environ.get('ADSENSE_SLOT', '').strip()}'")

    if inline:
        out = ROOT / "dist" / "ansanlife-inline.html"
        out.parent.mkdir(exist_ok=True)
    else:
        out = ROOT / "index.html"
    pwa = "" if inline else ('<link rel="manifest" href="manifest.webmanifest">\n'
                              '<link rel="icon" href="assets/icon-192.png" type="image/png">\n'
                              '<link rel="apple-touch-icon" href="assets/icon-180.png">\n'
                              '<meta name="apple-mobile-web-app-capable" content="yes">\n'
                              '<meta name="apple-mobile-web-app-title" content="안산살이">\n')
    ads_client = os.environ.get("ADSENSE_CLIENT", "").strip()
    if ads_client.startswith("ca-pub-"):
        # 애드센스 사이트 소유권 확인용 메타 태그
        pwa += f'<meta name="google-adsense-account" content="{ads_client}">\n'
    out.write_text(HEAD.replace("__PWA__", pwa) + html + TAIL, encoding="utf-8")
    # 관리 페이지 (공지 등록). Supabase 공개 키만 들어감
    if not inline:
        adm = (ROOT / "src" / "admin.template.html").read_text(encoding="utf-8")
        adm = adm.replace("'__SUPABASE_URL__'", f"'{sb_url}'").replace("'__SUPABASE_ANON_KEY__'", f"'{sb_key}'")
        (ROOT / "admin.html").write_text(adm, encoding="utf-8")
    print(f"built {out.relative_to(ROOT)}  (naver map: {'on' if key else 'off'}, google map: {'on' if gkey else 'off'}, api: {analyze or 'off'}, supabase: {'on' if sb_url and sb_key else 'off'})")


if __name__ == "__main__":
    main()
