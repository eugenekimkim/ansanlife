# 안산살이 (Ansan Life)

안산 거주 외국인 주민을 위한 다국어 생활 안내 모바일웹 프로토타입입니다.
분리배출, 버스·교통, 관공서, 병원, 공지·행사, 설문을 한곳에서 안내합니다.

- 운영 언어: 한국어 · English · Tiếng Việt (中文 · Русский · O‘zbekcha · Монгол 은 "준비 중")
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

## 사진 분석 켜기

"사진으로 물어보기"는 실시간 카메라로 찍은 사진을 분석 서버로 보내 배출 분류를 받습니다.
서버(`server/analyze-worker.js`)는 Claude API 이미지 입력을 쓰는 Cloudflare Worker 이고, 배포 방법은 [server/README.md](server/README.md) 에 있습니다.

```bash
NAVER_KEY=발급받은_Client_ID ANALYZE_URL=https://ansanlife-analyze.계정.workers.dev python3 build.py
```

`ANALYZE_URL` 없이 빌드하면 카메라·사진 선택은 그대로 되고, 결과는 "예시 결과" 표시와 함께 투명 페트병으로 나옵니다.

## 배포 (예: GitHub Pages)

저장소 Settings › Pages › Branch `main` / root 로 설정하면 `index.html` 이 바로 열립니다.
카메라 실시간 화면과 GPS 는 **HTTPS** 에서만 동작하므로 Pages 같은 HTTPS 호스팅에서 시험하세요.

## 폴더 구조

| 경로 | 내용 |
| --- | --- |
| `src/app.template.html` | 앱 원본 (CSS + JS 한 파일). 수정은 여기서 |
| `build.py` | 템플릿 → `index.html` 빌드, `--inline` 은 이미지 내장 단일 파일 |
| `index.html` | 빌드 결과 (네이버 키·분석 서버 없이 빌드됨) |
| `assets/` | 인트로 배경 이미지 (주황 노을, 하늘색), 원본 PNG |
| `server/` | 사진 분석 서버 (Cloudflare Worker + Claude API) |
| `docs/HANDOFF.md` | 인수인계 메모: 디자인 규칙, 구현 상태, 남은 일, 출처 |

## 코드 구조 한눈에

- 화면은 `SCR.<이름>()` 함수가 HTML 문자열을 돌려주는 방식 (`intro`, `home`, `w1`–`w6` 분리배출, `b1`–`b6` 교통, `hosp`, `hdetail`, `offices`, `news`, `surv`, `sq`, `sdone`)
- 상태는 `st` 객체, 화면 이동은 `go()` / `back()` / `home()`
- 문구는 `S.en` / `S.vi` / `S.ko` 사전
- 네이버 지도 연동: `NAVER_KEY`, `MAPS`, `mountMaps()`
- 네이버지도 앱/웹 열기: `openNaver()`, `nApp()`, `nWeb()`
- 집 주소: `st.addr`, 지역 변경 시트 `locSheet()`, 좌표→주소 `revGeo()`
- 카메라: `startCam()` / `capture()` / `stopCam()`, 사진 분석: `ANALYZE_URL`, `analyze()`, `runScan()`, 결과 분류 `DEST`

## 수정 후

`src/app.template.html` 을 고친 뒤 `python3 build.py` 로 `index.html` 을 다시 만들어 함께 커밋하세요.
