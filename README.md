# 안산살이 (Ansan Life)

안산 거주 외국인 주민을 위한 다국어 생활 안내 모바일웹 프로토타입입니다.
분리배출, 버스·교통, 관공서, 병원, 공지·행사, 설문을 한곳에서 안내합니다.

- 운영 언어: 한국어 · English · Tiếng Việt · 中文 · Русский · O‘zbekcha · Монгол (베트남어 이후 5개 언어는 AI 번역 · 원어민 검수 전)
- 디자인 시안: Figma "아이디어_안산시생활지원" (Page 1)
- 인수인계 메모: [docs/HANDOFF.md](docs/HANDOFF.md)

## 빠르게 실행하기

```bash
python3 build.py          # index.html 생성
python3 -m http.server    # http://localhost:8000 에서 확인
```

빌드 없이 보려면 저장소에 들어 있는 `index.html` 을 그대로 열어도 됩니다.

## 네이버 지도 켜기

1. 네이버 클라우드 콘솔 › Maps › Application 등록
   - **Dynamic Map**, **Geocoding**, **Reverse Geocoding** 체크 (Reverse Geocoding 은 GPS 로 동네를 바꿀 때 씀)
2. Web 서비스 URL 에 배포할 도메인 등록 (포트·경로 없이 호스트만)
3. 발급받은 Client ID 로 빌드

```bash
NAVER_KEY=발급받은_Client_ID python3 build.py
```

키가 없거나 인증에 실패하면 그림 지도가 대신 보여서 화면이 깨지지 않습니다.
지역 "변경"도 키 없이 동작하지만, 이때는 GPS 위치를 주소로 바꾸지 못해 주소를 직접 입력하게 안내합니다.

## API 서버 켜기 (사진 분석 · 버스 실시간 · 공지 번역)

`server/worker.js` 는 Cloudflare Worker 하나로 세 가지를 맡습니다. 배포 방법은 [server/README.md](server/README.md) 에 있습니다.

| 기능 | 필요한 키 (Worker secret) | 서버 없을 때 |
| --- | --- | --- |
| 사진으로 물어보기 | `ANTHROPIC_API_KEY` | 카메라는 동작, 결과는 "예시 결과" |
| 주변 정류장 · 도착 시간 | `DATA_GO_KR_KEY` | Sample 정류장·도착 시간 |
| 공지 번역 (`data/notices.json`) | `ANTHROPIC_API_KEY` + `NOTICES_URL` | 화면에 넣어 둔 예시 공지 |

```bash
NAVER_KEY=발급받은_Client_ID API_URL=https://ansanlife-api.계정.workers.dev python3 build.py
```

공지는 `data/notices.json` 에 **한국어 원문**으로 넣으면, 서버가 사용자의 언어로 번역하고(내용이 바뀔 때만) 앱에서 "원문 보기"로 한국어를 볼 수 있습니다.

## Supabase 켜기 (공지·광고 관리, 설문 저장)

공지·광고 등록과 설문 결과 확인은 Supabase 대시보드에서 합니다. 처음 설정과 운영 방법은 [supabase/README.md](supabase/README.md) 에 있습니다.

```bash
SUPABASE_URL=https://xxxx.supabase.co SUPABASE_ANON_KEY=<anon 키> python3 build.py
# 직접 광고가 없을 때 애드센스: ADSENSE_CLIENT=ca-pub-... ADSENSE_SLOT=...
```

Supabase 없이 빌드하면 예시 광고가 나오고, 설문 응답은 기기에만 남습니다.

## 버스 경로

목적지(자주 가는 곳 또는 주소 검색)를 고르면 **네이버지도 대중교통 길찾기**가 집 주소에서 출발하도록 열립니다(`nmap://route/public`). 네이버 키가 없거나 장소 이름이라 좌표를 못 찾으면 네이버지도 장소 검색으로 엽니다.

## 앱으로 설치 (PWA)

`manifest.webmanifest` 와 `sw.js` 가 함께 배포되면 휴대폰에서 "홈 화면에 추가"로 앱처럼 설치되고, 한 번 열었던 화면은 오프라인에서도 열립니다. 안드로이드는 홈에 설치 카드가 뜨고, 아이폰은 "공유 → 홈 화면에 추가" 안내가 뜹니다. `--inline` 단일 파일(아티팩트용)에서는 꺼집니다.

## 배포 (예: GitHub Pages)

저장소 Settings › Pages › Branch `main` / root 로 설정하면 `index.html` 이 바로 열립니다.
카메라 실시간 화면과 GPS 는 **HTTPS** 에서만 동작하므로 Pages 같은 HTTPS 호스팅에서 시험하세요.

## 폴더 구조

| 경로 | 내용 |
| --- | --- |
| `src/app.template.html` | 앱 원본 (CSS + JS 한 파일). 수정은 여기서 |
| `build.py` | 템플릿 → `index.html` 빌드, `--inline` 은 이미지 내장 단일 파일 |
| `index.html` | 빌드 결과. 지금은 Supabase(서울, 공개 키)만 연결해 빌드됨. 네이버 키·API 서버는 아직 |
| `manifest.webmanifest`, `sw.js` | 앱 설치(PWA) · 오프라인 |
| `data/notices.json` | Supabase 를 쓰기 전 임시 공지 원문 (서버가 번역) |
| `assets/` | 인트로 배경 이미지 (주황 노을, 하늘색), 원본 PNG, 앱 아이콘 |
| `server/` | API 서버 (Cloudflare Worker): 사진 분석, 경기도 버스, 공지 번역 |
| `supabase/` | DB 스키마·보안 규칙(`schema.sql`), 설정·운영 방법 |
| `docs/HANDOFF.md` | 인수인계 메모: 디자인 규칙, 구현 상태, 남은 일, 출처 |
| `docs/CHECKLIST.md` | 출시 전 확인·신청 목록 (안산시 문의, API 신청, 번역 검수) |
| `docs/PRIVACY_DRAFT.md` | 개인정보 처리·동의 문구 초안 (법률 검토용) |

## 코드 구조 한눈에

- 화면은 `SCR.<이름>()` 함수가 HTML 문자열을 돌려주는 방식 (`intro`, `home`, `w1`–`w6` 분리배출, `b1`–`b6` 교통, `hosp`, `hdetail`, `offices`, `news`, `surv`, `sq`, `sdone`)
- 상태는 `st` 객체, 화면 이동은 `go()` / `back()` / `home()`
- 문구는 `S.en` / `S.vi` / `S.ko` / `S.zh` / `S.ru` / `S.uz` / `S.mn` 사전 (키 226개, 모두 같은 구조)
- 네이버 지도 연동: `NAVER_KEY`, `MAPS`, `mountMaps()`
- 네이버지도 앱/웹 열기: `openNaver()`, `nApp()`, `nWeb()`
- 집 주소: `st.addr`, 지역 변경 시트 `locSheet()`, 좌표→주소 `revGeo()`
- 카메라: `startCam()` / `capture()` / `stopCam()`, 사진 분석: `API_URL`, `analyze()`, `runScan()`, 결과 분류 `DEST`
- 단지별 배출 요일: `st.rules`, `CITY`(안산시 기본값), `sched()`, 편집 화면 `SCR.rules`
- 버스 실시간: `loadStops()`, `loadArr()` (30초마다 갱신) · 경로: `PLACES`, `routeTo()` → 네이버지도 · 공지: `loadNews()`, `SCR.ndetail`
- Supabase: `sb()`, 광고 `adSlot()`/`loadAd()`(직접 → 애드센스), 설문 `saveSurvey()`(실패 시 기기에 모았다 재전송)
- 언어: `COUNTRIES`, `S.<언어>`, `DAYS`, `DAYLONG`, `LOCALE` (키릴·중국어는 `.l-ru/.l-mn/.l-zh` 글꼴)

## 수정 후

`src/app.template.html` 을 고친 뒤 `python3 build.py` 로 `index.html` 을 다시 만들어 함께 커밋하세요.
