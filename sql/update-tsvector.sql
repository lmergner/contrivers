/*
 * 1. Update tsvector column on existing database.
 * 2. Create a trigger to auto update ts_vector column
 */

BEGIN;

alter writing add column tsvector tsvector EXCEPTION WHEN duplicate_column THEN RAISE NOTICE 'column tsvector already exists in writing.';
update writing set tsvector = to_tsvector('english', coalesce(title, '') || '' || coalesce(text, ''));
create trigger ts_update before insert or update on writing for each row execute procedure tsvector_update_trigger(tsvector, 'pg_catalog.english', 'title', 'text');
create index tsvector_idx on writing using gin(tsvector);

END;

