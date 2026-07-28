create extension if not exists pgcrypto;

create table if not exists public.articles (
  id uuid primary key default gen_random_uuid(),
  source_url text not null unique,
  naver_url text,
  publisher_title text not null,
  category text not null,
  published_at_text text,
  collected_date date not null,
  source_text text not null,
  study_data jsonb not null,
  created_at timestamptz not null default now()
);

alter table public.articles enable row level security;

-- The app can read articles with the anon key.
create policy "public read articles"
on public.articles for select
to anon
using (true);

-- Writes are performed only with the service-role key in GitHub Actions.
create index if not exists articles_collected_date_idx on public.articles (collected_date desc);
create index if not exists articles_category_idx on public.articles (category);
