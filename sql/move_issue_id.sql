/*
 * move_issue_id.sql
 * Copyright (C) 2014 lmergner <gmail.com>
 *
 * Distributed under terms of the MIT license.
 */

BEGIN;

alter table writing add column issue_id integer;

insert into writing (issue_id) values (select article.issue_id from article, writing where article.id = writing.id and article.issue_id is not null);

alter table article drop column issue_id;

END;

/* select article.issue_id, article.id, writing.id as writ_id, writing.issue_id art_id from article, writing where article.id=writing.id and article.issue_id is not null; */
-- vim:et
