/*
 * queries.sql
 * Copyright (C) 2014 lmergner <gmail.com>
 *
 * Distributed under terms of the MIT license.
 */


/* Select all writings and tags */
select writing.title, tag.name from writing, tag, tag_to_writing where tag_to_writing.tag_id = tag.id and tag_to_writing.writing_id = writing.id;

select title from writing inner join tag_to_writing on writing.id = tag_to_writing.writing_id inner join tag on tag.id = tag_to_writing.tag_id where tag.name = 'Technology';
-- vim:et
