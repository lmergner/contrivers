-- Test changes to isbn column
-- Revision ID: 2d2fd2398328

BEGIN;
    --- BOOKS
    SELECT plan(10);

    SELECT has_column('book', 'edition', 'book should have col edition');
    SELECT has_column('book', 'editors', 'book should have col editors');
    SELECT has_column('book', 'translator', 'book should have col translator');

    SELECT is_empty('SELECT * FROM book WHERE isbn_10 IS NULL;', 'No existing book review should have a null isbn_10');
    SELECT col_type_is('book', 'isbn_10', 'character varying(10)', 'Book isbn_10 should be var_char not integer, so that leading zeros are not truncated');
    SELECT col_type_is('book', 'isbn_13', 'character varying(13)', 'Book isbn_10 should be var_char not integer, so that leading zeros are not truncated');
    SELECT is_empty('SELECT * from BOOK where length(isbn_13) != 13', 'isbn_13 should be 13 characters long');
    SELECT is_empty('SELECT * from BOOK where length(isbn_10) != 10', 'isbn_10 should be 10 characters long');
    SELECT col_has_check('book', 'isbn_10', 'book col isbn_10 should have a check constraint of 10 chars');
    SELECT col_has_check('book', 'isbn_13', 'book column isbn_13 should have a check constraint of 13 chars');

    SELECT * from finish();
ROLLBACK;
