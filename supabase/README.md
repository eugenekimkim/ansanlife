# Supabase 설정 · 운영

안산살이는 Supabase를 **공지·광고 관리**와 **설문 응답 저장**에 씁니다. 별도 관리자 화면 대신 Supabase 대시보드의 **Table Editor**가 관리 화면입니다.

## 1. 처음 설정 (10분)

1. [supabase.com](https://supabase.com) 가입 → **New project**
   - Region: **Northeast Asia (Seoul)** 를 고르세요 (개인정보 국외 이전을 줄이기 위해).
   - Database password 는 안전한 곳에 보관.
2. 왼쪽 **SQL Editor** → `supabase/schema.sql` 내용을 통째로 붙여 넣고 **Run**. 다시 실행해도 안전합니다.
3. **Project Settings › API** 에서 두 값을 복사합니다.
   - Project URL (`https://xxxx.supabase.co`)
   - **anon / publishable** 키 (공개용). `service_role` / secret 키는 **절대** 앱이나 이 저장소에 넣지 마세요.
4. 앱 빌드에 넣습니다.
   ```bash
   SUPABASE_URL=https://xxxx.supabase.co SUPABASE_ANON_KEY=<anon 키> \
   NAVER_KEY=... API_URL=... python3 build.py
   ```
5. 공지 번역을 Supabase 에서 읽게 하려면 `server/wrangler.toml` 의 `NOTICES_URL` 을 아래로 바꾸고 `NOTICES_KEY` 에 같은 anon 키를 넣은 뒤 `npx wrangler deploy`.
   ```
   https://xxxx.supabase.co/rest/v1/notices?select=id,type,title,body,date,url,sample&published=is.true&order=sort.desc,created_at.desc
   ```

## 2. 매일 운영 (Table Editor)

| 하고 싶은 일 | 표 | 방법 |
| --- | --- | --- |
| 공지·행사 올리기 | `notices` | Insert row → `title`, `body` 를 **한국어로** 입력, `type` 은 official(공지) / event(행사), `published` 를 true 로. 번역은 자동 |
| 공지 내리기 | `notices` | `published` 를 false 로 |
| 위로 올리기 | `notices` | `sort` 숫자를 크게 |
| 예시 공지 지우기 | `notices` | `sample` 이 true 인 행 삭제 |
| 광고 등록 | `ads` | `advertiser`(관리용), `langs`(보여줄 언어, 예: `{vi}` 베트남어만, `{ru,uz}`), `title`(최대 80자, 그 언어로), `body`(최대 160자), `url`(https), `image_url`(https, 정사각형), `starts_at`/`ends_at`(기간) |
| 광고 잠시 끄기 | `ads` | `active` 를 false 로 |
| 광고 노출 비율 | `ads` | 같은 언어에 여러 개면 `weight` 비율로 무작위 노출 |
| 설문 결과 보기 | `survey_responses` | 표에서 보거나 **Export to CSV**. `answers` 는 문항별 선택 코드(예: `["van","bus","week"]`) |

언어 코드: `en` 영어 · `vi` 베트남어 · `ko` 한국어 · `zh` 중국어 · `ru` 러시아어 · `uz` 우즈베크어 · `mn` 몽골어

## 3. 보안 규칙 (schema.sql 에 들어 있음)

앱이 쓰는 공개 키로 할 수 있는 일은 세 가지뿐입니다. 로컬 Postgres 16 에서 확인했습니다.

- 게시된(`published`) 공지 읽기
- 지금 노출 중인(`active`, 기간 안) 광고 읽기 — `advertiser` 열은 못 읽음
- 설문 응답 **쓰기** — 읽기·수정·삭제는 못 함, 언어 코드·크기 검사

등록·수정·조회는 대시보드에 로그인한 관리자만 할 수 있습니다. 운영자를 늘리려면 **Project Settings › Team** 에서 초대하세요.

## 4. 광고 네트워크 (선택)

직접 계약 광고가 없는 언어에는 애드센스가 대신 나옵니다. 애드센스 승인 후 빌드에 넣으세요.

```bash
ADSENSE_CLIENT=ca-pub-xxxxxxxxxxxx ADSENSE_SLOT=xxxxxxxxxx python3 build.py
```

광고 제거(설문 보상) 중에는 직접 광고·애드센스 모두 숨깁니다. 애드센스는 쿠키를 쓰므로 개인정보 처리방침에 적어야 합니다(`docs/PRIVACY_DRAFT.md`).
