-- Check the database settings

BEGIN;
    SELECT plan(1);
    SELECT results_eq('SHOW timezone;', ARRAY['UTC']);

    SELECT * from finish();
ROLLBACK;
