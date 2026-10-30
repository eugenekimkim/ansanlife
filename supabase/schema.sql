-- 안산살이 Supabase 스키마
-- Supabase 대시보드 › SQL Editor 에 통째로 붙여 넣고 Run.
-- 앱은 공개(anon) 키로만 접근합니다. 아래 RLS 정책 때문에 앱이 할 수 있는 일은
--   · 게시된 공지 읽기 · 지금 노출 중인 광고 읽기 · 설문 응답 "쓰기"(읽기 불가)
-- 뿐이고, 등록·수정·응답 조회는 대시보드(Table Editor)에서 관리자만 합니다.

create extension if not exists pgcrypto;

-- ---------- 공지·행사 (한국어 원문만. 번역은 API 서버가 함) ----------
create table if not exists public.notices (
  id          uuid primary key default gen_random_uuid(),
  type        text not null default 'official' check (type in ('official', 'event')),
  title       text not null check (char_length(title) between 1 and 300),
  body        text not null default '' check (char_length(body) <= 4000),
  date        date,                       -- 행사일·게시일 (선택)
  url         text check (url is null or url ~ '^https://'),
  published   boolean not null default false,  -- true 로 바꾸면 앱에 보임
  sample      boolean not null default false,
  sort        integer not null default 0,      -- 클수록 위
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
alter table public.notices enable row level security;
drop policy if exists "notices: read published" on public.notices;
create policy "notices: read published" on public.notices for select to anon, authenticated using (published);

-- ---------- 광고 (직접 계약) ----------
create table if not exists public.ads (
  id          uuid primary key default gen_random_uuid(),
  advertiser  text not null,                -- 관리용 (앱에 안 보임)
  langs       text[] not null default '{en,vi,ko,zh,ru,uz,mn}',  -- 보여줄 언어 (국적 타깃)
  title       text not null check (char_length(title) between 1 and 80),
  body        text not null default '' check (char_length(body) <= 160),
  url         text check (url is null or url ~ '^https://'),
  image_url   text check (image_url is null or image_url ~ '^https://'),
  weight      integer not null default 1 check (weight between 1 and 100),  -- 여러 개면 비율
  active      boolean not null default true,
  starts_at   timestamptz,
  ends_at     timestamptz,
  created_at  timestamptz not null default now()
);
alter table public.ads enable row level security;
drop policy if exists "ads: read running" on public.ads;
create policy "ads: read running" on public.ads for select to anon, authenticated
  using (active and (starts_at is null or starts_at <= now()) and (ends_at is null or ends_at >= now()));
create index if not exists ads_langs_idx on public.ads using gin (langs);

-- ---------- 설문 응답 (쓰기만, 개인 식별 정보 없음) ----------
create table if not exists public.survey_responses (
  id          bigint generated always as identity primary key,
  survey_id   text not null check (char_length(survey_id) <= 40),
  lang        text not null check (lang in ('en','vi','ko','zh','ru','uz','mn')),
  answers     jsonb not null check (jsonb_typeof(answers) = 'array' and jsonb_array_length(answers) <= 20 and pg_column_size(answers) < 2000),
  created_at  timestamptz not null default now()
);
alter table public.survey_responses enable row level security;
drop policy if exists "survey: insert only" on public.survey_responses;
create policy "survey: insert only" on public.survey_responses for insert to anon, authenticated with check (true);
-- select 정책이 없으므로 앱(anon)은 응답을 읽을 수 없음. 대시보드에서만 조회.

-- 공개 키로 다른 표를 만들거나 지우지 못하게 (기본값 확인용)
revoke all on public.notices, public.ads, public.survey_responses from anon;
grant select on public.notices to anon, authenticated;
grant select (id, langs, title, body, url, image_url, weight, active, starts_at, ends_at) on public.ads to anon, authenticated;  -- advertiser 는 숨김
grant insert (survey_id, lang, answers) on public.survey_responses to anon, authenticated;

-- 수정 시각 자동 갱신
create or replace function public.touch_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;
drop trigger if exists notices_touch on public.notices;
create trigger notices_touch before update on public.notices for each row execute function public.touch_updated_at();

-- 예시 데이터 (앱 화면 확인용. 실제 운영 전 지우거나 published=false 로)
insert into public.notices (type, title, body, published, sample, sort)
select * from (values
  ('official', '외국인 주민 무료 한국어 교실', '예시 공지입니다. 실제 공지를 한국어 원문 그대로 넣으면 앱이 사용자의 언어로 번역해 보여줍니다.', true, true, 2),
  ('event', '근로자 주말 건강검진', '예시 행사입니다. 장소, 날짜, 시간, 신청 방법을 한국어로 적어 주세요.', true, true, 1)
) v(type, title, body, published, sample, sort)
where not exists (select 1 from public.notices);   -- 처음 한 번만
