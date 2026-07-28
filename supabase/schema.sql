create extension if not exists pgcrypto;
create table if not exists public.articles (
  id uuid primary key default gen_random_uuid(),
  source_url text not null unique,
  naver_url text,
  publisher_name text,
  publisher_title text,
  category text,
  author_name text,
  published_at timestamptz,
  published_at_text text,
  collected_date date not null default current_date,
  source_text text,
  source_text_hash text,
  study_data jsonb not null default '{}'::jsonb,
  processing_status text not null default 'pending',
  processing_error text,
  ai_model text,
  is_published boolean not null default true,
  created_at timestamptz not null default now()
);
alter table public.articles enable row level security;
drop policy if exists "Public can read published articles" on public.articles;
create policy "Public can read published articles" on public.articles for select to anon using (is_published = true);
