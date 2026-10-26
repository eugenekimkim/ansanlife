-- 안산살이 관리자 권한 (관리 페이지 admin.html 용)
-- schema.sql 다음에 SQL Editor 에서 실행. 다시 실행해도 안전합니다.
--
-- 관리자 = Supabase Auth 로 로그인 + admins 표에 등록된 사람.
-- 로그인만 하고 admins 에 없으면 일반 방문자와 똑같이 아무것도 못 바꿉니다.

create table if not exists public.admins (
  user_id    uuid primary key references auth.users (id) on delete cascade,
  note       text,                                  -- 누구인지 메모
  created_at timestamptz not null default now()
);
alter table public.admins enable row level security;
revoke all on public.admins from anon, authenticated;
grant select on public.admins to authenticated;
drop policy if exists "admins: see self" on public.admins;
create policy "admins: see self" on public.admins for select to authenticated using (user_id = auth.uid());

-- 정책에서 쓰는 검사 함수 (admins 표의 RLS 를 거치지 않도록 security definer)
create or replace function public.is_admin() returns boolean
  language sql stable security definer set search_path = public, pg_temp
as $$ select exists (select 1 from public.admins where user_id = auth.uid()) $$;
revoke all on function public.is_admin() from public;
grant execute on function public.is_admin() to anon, authenticated;

-- 공지: 관리자는 게시 안 된 것까지 보고, 쓰고, 고치고, 지움
grant select, insert, update, delete on public.notices to authenticated;
drop policy if exists "notices: admin all" on public.notices;
create policy "notices: admin all" on public.notices for all to authenticated
  using (public.is_admin()) with check (public.is_admin());

-- 광고: 관리자 전체 관리 (advertiser 열 포함)
grant select, insert, update, delete on public.ads to authenticated;
drop policy if exists "ads: admin all" on public.ads;
create policy "ads: admin all" on public.ads for all to authenticated
  using (public.is_admin()) with check (public.is_admin());

-- 설문 응답: 관리자만 조회
grant select on public.survey_responses to authenticated;
drop policy if exists "survey: admin read" on public.survey_responses;
create policy "survey: admin read" on public.survey_responses for select to authenticated using (public.is_admin());

-- 관리자 등록 예시: Authentication › Users 에서 사용자를 만든 뒤
--   insert into public.admins (user_id, note)
--   select id, '대표' from auth.users where email = 'you@example.com'
--   on conflict do nothing;
