BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL
);

-- Running upgrade None -> 203dfa6493b5

CREATE TABLE key_value (
    key VARCHAR NOT NULL, 
    value JSON, 
    PRIMARY KEY (key), 
    UNIQUE (key)
);

CREATE TABLE image (
    id SERIAL NOT NULL, 
    filename VARCHAR, 
    url VARCHAR, 
    expired BOOLEAN, 
    PRIMARY KEY (id)
);

CREATE TABLE template (
    id SERIAL NOT NULL, 
    filename VARCHAR NOT NULL, 
    html VARCHAR NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE image_to_writing (
    image_id INTEGER, 
    writing_id INTEGER, 
    FOREIGN KEY(image_id) REFERENCES image (id), 
    FOREIGN KEY(writing_id) REFERENCES writing (id)
);

CREATE TABLE writing_to_writing (
    response_id INTEGER NOT NULL, 
    respondee_id INTEGER NOT NULL, 
    PRIMARY KEY (response_id, respondee_id), 
    FOREIGN KEY(respondee_id) REFERENCES writing (id), 
    FOREIGN KEY(response_id) REFERENCES writing (id)
);

CREATE TABLE book (
    id SERIAL NOT NULL, 
    title VARCHAR, 
    subtitle VARCHAR, 
    author VARCHAR, 
    publisher VARCHAR, 
    city VARCHAR, 
    year INTEGER, 
    isbn_10 INTEGER, 
    isbn_13 VARCHAR, 
    pages INTEGER, 
    price FLOAT, 
    review_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(review_id) REFERENCES review (id)
);

DROP TABLE response;

DROP TABLE post;

ALTER TABLE article DROP COLUMN position;

ALTER TABLE writing ADD COLUMN issue_id INTEGER;

ALTER TABLE article DROP COLUMN issue_id;

update writing set issue_id = 1 where id in (1, 2, 3, 4);;

ALTER TABLE author ADD COLUMN bio VARCHAR;

ALTER TABLE author ADD COLUMN hidden BOOLEAN;

ALTER TABLE author DROP COLUMN profile_photo;

ALTER TABLE author ALTER COLUMN email SET NOT NULL;

ALTER TABLE author DROP CONSTRAINT author_name_key;

ALTER TABLE issue DROP COLUMN publish_date;

ALTER TABLE issue DROP COLUMN description;

ALTER TABLE review DROP COLUMN book_reviewed;

ALTER TABLE writing ADD COLUMN tsvector TSVECTOR;

ALTER TABLE writing DROP COLUMN extras;

update writing set tsvector = to_tsvector('english', coalesce(title, '') || '' || coalesce(text, ''));;

create trigger ts_update before insert or update on writing for each row execute procedure tsvector_update_trigger(tsvector, 'pg_catalog.english', 'title', 'text');;

create index tsvector_idx on writing using gin(tsvector);;

INSERT INTO alembic_version (version_num) VALUES ('203dfa6493b5');

COMMIT;

