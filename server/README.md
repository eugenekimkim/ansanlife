# 사진 분석 서버

앱의 "사진으로 물어보기"가 찍은 사진을 받아 Claude API(이미지 입력)로 품목을 판별하고, 안산시 배출 분류 하나를 돌려주는 Cloudflare Worker 입니다.

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
npx wrangler secret put ANTHROPIC_API_KEY      # 키 붙여넣기
# wrangler.toml 의 ALLOWED_ORIGIN 을 앱 주소로 바꾼 뒤
npx wrangler deploy
```

배포가 끝나면 나오는 `https://ansanlife-analyze.<계정>.workers.dev` 주소를 앱 빌드에 넣습니다.

```bash
cd ..
ANALYZE_URL=https://ansanlife-analyze.<계정>.workers.dev NAVER_KEY=... python3 build.py
```

## 요청과 응답

```
POST /   { "image": "<base64>", "mediaType": "image/jpeg", "lang": "vi" }
200      { "dest": "rec", "name": "Lon nhôm", "name_ko": "알루미늄 캔", "confidence": 0.86, "candidates": [] }
```

오류는 `{ "error": "..." }` 와 4xx/5xx 로 돌아오고, 앱은 "사진을 분석하지 못했어요 · 다시 찍기 / 직접 고르기"를 보여줍니다.

## 설정

| 이름 | 필수 | 내용 |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | 예 (secret) | Claude API 키 |
| `ALLOWED_ORIGIN` | 예 | 앱 주소. 여러 개면 쉼표로 구분 (예: `https://eugenekimkim.github.io,http://localhost:8000`) |
| `MODEL` | 아니오 | 기본 `claude-sonnet-5-5`. 비용을 줄이려면 `claude-haiku-5-5` 로 시험 |

## 출시 전 확인

- `RULES` 의 분류 설명과 예시는 일반적인 분리배출 기준으로 적은 것입니다. 안산시 자원순환과(031-481-2259)에 확인한 뒤 고치세요. 분류를 바꾸면 앱의 `DEST` 도 함께 고쳐야 합니다.
- 사진 수집·전송에 대한 동의 문구(모국어)를 개인정보 검토 때 함께 확인하세요.
- 무료 플랜 요청 한도와 Claude API 사용량 상한(콘솔의 Spend limit)을 정해 두세요.
