-- alembic migration tests
-- Revision ID: 5703f85b3a6a
-- Revises: 2d2fd2398328
-- Create Date: 2015-07-30 22:14:00.662051
BEGIN;
    SELECT plan(2);

    SELECT hasnt_column('writing', 'issue_num', 'writing should no longer have an issue_num column');
    SELECT hasnt_table('issue', 'issue table should be deleted');

    SELECT * from finish();
ROLLBACK;
