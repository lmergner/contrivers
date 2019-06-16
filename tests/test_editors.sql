
BEGIN;
    SELECT plan(13);

    SELECT hasnt_table('admin', 'table admin should be renamed');
    SELECT has_table('editors', 'db should have table editors');

    SELECT columns_are('editors', ARRAY['id', 'username', 'email', 'password', 'author_id', 'create_date', 'password_updated', 'last_edited_date']);
    SELECT col_is_pk('editors', 'id');
    SELECT col_not_null('editors', 'password', 'editors.password should be not null');
    SELECT col_not_null('editors', 'email', 'editors.email should be not null');
    SELECT col_is_unique('editors', 'email', 'editors.email should be unique');
    SELECT col_is_fk('editors', 'author_id', 'editors.author_id should be a foreign key');
    SELECT has_index('editors', 'admin_pkey', 'editors pk is the old admin_pkey');
    SELECT has_index('editors', 'editors_email_key');


    -- DATES
    SELECT col_type_is('editors', 'password_updated', 'timestamp with time zone');
    SELECT col_type_is('editors', 'last_edited_date', 'timestamp with time zone');
    SELECT col_type_is('editors', 'create_date', 'timestamp with time zone');


    SELECT * from finish();
ROLLBACK;
