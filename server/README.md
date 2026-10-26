# API 서버 (Cloudflare Worker)

`worker.js` 하나로 세 가지를 맡습니다.

| 경로 | 하는 일 | 필요한 secret |
| --- | --- | --- |
| `POST /analyze` (또는 `/`) | 사진 → 배출 분류 (Claude API 이미지 입력) | `ANTHROPIC_API_KEY` |
| `GET /bus/stops?lat=&lng=` | 주변 정류장 최대 8곳 (경기도 정류소 조회 v2) | `DATA_GO_KR_KEY` |
| `GET /bus/arrivals?stationId=` | 정류장 도착 정보 (경기도 버스도착정보 v2) | `DATA_GO_KR_KEY` |
| `GET /notices?lang=vi` | `NOTICES_URL` 의 한국어 공지를 번역해 원문과 함께 | `ANTHROPIC_API_KEY` |

모든 경로는 `ALLOWED_ORIGIN` 에 등록한 주소에서 온 요청만 받습니다. 키가 없는 기능은 503 을 돌려주고, 앱은 예시 데이터로 대신 보여줍니다.

## 사진 분석

앱의 "사진으로 물어보기"가 찍은 사진을 받아 Claude API(이미지 입력)로 품목을 판별하고, 안산시 배출 분류 하나를 돌려줍니다.

- 사진은 저장·기록하지 않고 메모리에서만 처리합니다.
- 판별은 `RULES` 표의 8개 분류로만 제한합니다: `pet` 투명 페트병 · `rec` 재활용 · `food` 음식물 · `gen` 일반 · `glass` 깨진 유리 · `bat` 건전지·형광등 · `bulky` 대형폐기물 · `unknown` 판단 불가
- 배출 요일·봉투·주의사항은 서버가 아니라 앱이 안산시 기준으로 보여줍니다. 서버는 "무엇인지, 어느 분류인지"만 답합니다.
- 자신 없으면(confidence < 0.6) 후보를 최대 3개 함께 보내고, 앱이 "혹시 이 중 하나인가요?"로 묻습니다.
- `ALLOWED_ORIGIN` 에 등록한 주소에서 온 요청만 받습니다(다른 사이트가 API 키를 쓰지 못하게).

## 배포

필요한 것: Cloudflare 계정(무료), Claude API 키(console.anthropic.com).

```bash
cd server
npx wrangler login
npx wrangler secret put ANTHROPIC_API_KEY      # Claude API 키
npx wrangler secret put DATA_GO_KR_KEY         # 공공데이터포털 인증키 (Decoding 키)
# wrangler.toml 의 ALLOWED_ORIGIN, NOTICES_URL 을 앱 주소에 맞게 바꾼 뒤
npx wrangler deploy
```

배포가 끝나면 나오는 `https://ansanlife-api.<계정>.workers.dev` 주소를 앱 빌드에 넣습니다.

```bash
cd ..
API_URL=https://ansanlife-api.<계정>.workers.dev NAVER_KEY=... python3 build.py
```

## 요청과 응답

```
POST /analyze   { "image": "<base64>", "mediaType": "image/jpeg", "lang": "vi" }
200      { "dest": "rec", "name": "Lon nhôm", "name_ko": "알루미늄 캔", "confidence": 0.86, "candidates": [] }
```

오류는 `{ "error": "..." }` 와 4xx/5xx 로 돌아오고, 앱은 "사진을 분석하지 못했어요 · 다시 찍기 / 직접 고르기"를 보여줍니다.

## 설정

| 이름 | 필수 | 내용 |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | 예 (secret) | Claude API 키 |
| `ALLOWED_ORIGIN` | 예 | 앱 주소. 여러 개면 쉼표로 구분 (예: `https://eugenekimkim.github.io,http://localhost:8000`) |
| `MODEL` | 아니오 | 기본 `claude-haiku-5-5` (사진 분석·공지 번역) |
| `VISION_MODEL` | 아니오 | 사진 분석만 다른 모델로. 정확도가 부족하면 `claude-sonnet-5-5` (약 20배 비쌈) |
| `TR_KV` | 아니오 (KV 바인딩) | 공지 번역 저장소. 있으면 전 세계 공유로 30일 보관, 없으면 데이터센터별 Cache API |
| `DATA_GO_KR_KEY` | 버스 기능 (secret) | 공공데이터포털 인증키(Decoding). 경기도 버스도착정보·정류소 조회 v2 활용 신청 필요 |
| `NOTICES_URL` | 공지 기능 | Supabase `notices` REST 주소(`supabase/README.md`) 또는 `data/notices.json` 주소 |
| `NOTICES_KEY` | Supabase 공지일 때 | Supabase anon(공개) 키 |

## 버스 · 공지 응답

```
GET /bus/stops?lat=37.32&lng=126.80
200 { "stops": [ { "id": "224000123", "name": "초지역", "no": "37123", "dist": 120, "lat": 37.32, "lng": 126.807 } ] }

GET /bus/arrivals?stationId=224000123
200 { "stationId": "224000123", "at": 1793025386745, "arrivals": [
      { "route": "99", "dest": "안산역", "type": 13, "ended": false,
        "buses": [ { "min": 7, "stops": 3, "crowd": 2, "seats": null, "low": false } ] } ] }

GET /notices?lang=vi
200 { "lang": "vi", "notices": [ { "id": "...", "title": "(번역)", "body": "(번역)", "title_ko": "...", "body_ko": "...", "type": "official", "date": null, "url": null } ] }
```

경기도 버스 API 응답은 공식 매뉴얼의 필드명(`predictTime1`, `locationNo1`, `crowded1`, `remainSeatCnt1`, `flag` 등)을 기준으로 바꿉니다. 실제 키로 **첫 호출 때 응답 구조를 한 번 확인**하세요(`mapArrivals`, `mapStops`). 목록이 1건이면 객체로 오는 경우도 처리합니다.

## 예상 비용 (2026-10 요금표 기준, 1달러 ≈ 1,400원)

| | Haiku 5.5 (기본) | Sonnet 5.5 |
| --- | --- | --- |
| 사진 1장 (입력 약 2,000·출력 약 150토큰) | 약 0.4원 | 약 8원 |
| 월 사용자 1만 명 × 4장 | 약 1.5만 원 | 약 31만 원 |
| 공지 번역 | 공지 1건 × 6개 언어를 **처음 한 번만** (같은 내용은 30일 재사용) → 월 수백 원 수준 | 공지 1건 × 6개 언어 약 65원 |

사진은 앱이 긴 변 1024px JPEG 로 줄여 보내므로 장당 약 1,036 이미지 토큰입니다. Anthropic 콘솔에서 **월 사용 상한(Spend limit)** 을 꼭 정하세요.

## 출시 전 확인

- 모델 정하기: 실제 쓰레기 사진 50장 정도로 Haiku 와 Sonnet 을 비교해 `VISION_MODEL` 결정

- 버스: 실제 키로 `/bus/stops`, `/bus/arrivals` 를 한 번씩 불러 필드가 맞는지 확인

- `RULES` 의 분류 설명과 예시는 일반적인 분리배출 기준으로 적은 것입니다. 안산시 자원순환과(031-481-2259)에 확인한 뒤 고치세요. 분류를 바꾸면 앱의 `DEST` 도 함께 고쳐야 합니다.
- 사진 수집·전송에 대한 동의 문구(모국어)를 개인정보 검토 때 함께 확인하세요.
- 무료 플랜 요청 한도와 Claude API 사용량 상한(콘솔의 Spend limit)을 정해 두세요.
