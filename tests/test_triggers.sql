-- Check the tsvector trigger

BEGIN;
    SELECT plan(3);

    SELECT schemas_are(ARRAY[ 'public' ]);
    SELECT triggers_are('writing', ARRAY['ts_update']);
    SELECT indexes_are('writing', ARRAY['tsvector_idx', 'writing_pkey']);

    SELECT * from finish();
ROLLBACK;


