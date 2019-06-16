-- Table schema tests

BEGIN;
    SELECT plan(19);
    SELECT has_table('writing');
    SELECT has_table('article');
    SELECT has_table('review');
    SELECT has_table('author');
    SELECT has_table('book');
    SELECT has_table('image');

    -- Issues should be going away
    SELECT hasnt_table('issue');
    SELECT hasnt_table('key_value');
    SELECT hasnt_table('template');

    SELECT has_column('writing', 'title');
    SELECT has_column('writing', 'text');
    SELECT has_column('writing', 'hidden');
    SELECT col_type_is('writing', 'hidden', 'boolean');
    SELECT has_column('writing', 'publish_date', 'writing table should have a publish_date column');
    SELECT col_type_is('writing', 'publish_date', 'timestamp with time zone', 'publish_date should be a DateTime with timezone');
    SELECT is_empty('SELECT * FROM WRITING WHERE publish_date IS NULL;', 'writing publish_date should not be null for existing articles');

    -- Tags
    SELECT col_is_unique('tag', 'name', 'tags.name should be unique');

    -- writing.slug
    SELECT has_column('writing', 'slug');
    SELECT col_type_is('writing', 'slug', 'character varying(250)');

    SELECT * from finish();
ROLLBACK;
