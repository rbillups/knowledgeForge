create extension if not exists vector;

create table if not exists knowledge_collections (
    id bigint generated always as identity primary key,
    slug text not null unique,
    name text not null,
    description text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists documents (
    id bigint generated always as identity primary key,
    collection_id bigint not null references knowledge_collections(id) on delete cascade,
    filename text not null,
    title text not null,
    file_type text not null,
    source_type text not null default 'upload',
    status text not null default 'uploaded',
    page_count integer,
    chunk_count integer not null default 0,
    error_message text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint documents_status_check
        check (status in ('uploaded', 'processing', 'indexed', 'failed')),

    constraint documents_source_type_check
        check (source_type in ('upload', 'portfolio', 'github', 'manual'))
);

create table if not exists document_chunks (
    id bigint generated always as identity primary key,
    document_id bigint not null references documents(id) on delete cascade,
    chunk_index integer not null,
    content text not null,
    page_number integer,
    token_estimate integer,
    embedding vector(1536),
    created_at timestamptz not null default now(),

    constraint document_chunks_unique_index
        unique (document_id, chunk_index)
);

create table if not exists document_feedback (
    id bigint generated always as identity primary key,
    document_id bigint references documents(id) on delete set null,
    question text,
    answer text,
    rating text,
    notes text,
    created_at timestamptz not null default now(),

    constraint document_feedback_rating_check
        check (rating in ('helpful', 'not_helpful'))
);

insert into knowledge_collections (slug, name, description)
values (
    'portfolio',
    'Portfolio Knowledge Base',
    'Public professional background, projects, skills, and case studies.'
)
on conflict (slug) do nothing;