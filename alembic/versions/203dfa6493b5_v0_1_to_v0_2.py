"""v0.1 to v0.2

Revision ID: 203dfa6493b5
Revises: None
Create Date: 2014-12-02 15:46:36.413704

"""

# revision identifiers, used by Alembic.
revision = '203dfa6493b5'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql
import logging

logger = logging.getLogger(__name__)

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('key_value',
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('value', postgresql.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('key'),
    sa.UniqueConstraint('key')
    )
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('expired', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('template',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(), nullable=False),
    sa.Column('html', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('image_to_writing',
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.Column('writing_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['image.id'], ),
    sa.ForeignKeyConstraint(['writing_id'], ['writing.id'], )
    )
    op.create_table('writing_to_writing',
    sa.Column('response_id', sa.Integer(), nullable=False),
    sa.Column('respondee_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['respondee_id'], ['writing.id'], ),
    sa.ForeignKeyConstraint(['response_id'], ['writing.id'], ),
    sa.PrimaryKeyConstraint('response_id', 'respondee_id')
    )

    op.create_table('book',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('subtitle', sa.String(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('publisher', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('isbn_10', sa.Integer(), nullable=True),
    sa.Column('isbn_13', sa.String(), nullable=True),
    sa.Column('pages', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('review_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['review_id'], ['review.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('response')
    op.drop_table('post')
    op.drop_column(u'article', 'position')

    # Issue_id
    op.add_column(u'writing', sa.Column('issue_id', sa.Integer(), nullable=True))
    op.drop_column(u'article', 'issue_id')
    op.execute(u'update writing set issue_id = 1 where id in (1, 2, 3, 4);')
    logger.warn('Manually setting the issue_id for the first issues. This will fail if there are more issues past Dec. 2014.')

    op.add_column(u'author', sa.Column('bio', sa.String(), nullable=True))
    op.add_column(u'author', sa.Column('hidden', sa.Boolean(), nullable=True))
    op.drop_column(u'author', 'profile_photo')

    op.alter_column(u'author', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_constraint('author_name_key', 'author')
    # op.drop_index('author_name_key', table_name='author')
    # the above commands fail so just do it in straight sql
    # op.execute('alter table author drop constraint if exists author_name_key;')

    op.drop_column(u'issue', u'publish_date')
    op.drop_column(u'issue', 'description')
    op.drop_column(u'review', u'book_reviewed')
    op.add_column(u'writing', sa.Column('tsvector', postgresql.TSVECTOR(), nullable=True))
    op.drop_column(u'writing', u'extras')
    ### end Alembic commands ###

    ### Setup tsvector
    tsv_update_sql = text("update writing set tsvector = to_tsvector('english', coalesce(title, '') || '' || coalesce(text, ''));")
    tsv_create_trigger = text("create trigger ts_update before insert or update on writing for each row execute procedure tsvector_update_trigger(tsvector, 'pg_catalog.english', 'title', 'text');")
    tsv_create_index = text("create index tsvector_idx on writing using gin(tsvector);")
    op.execute(tsv_update_sql)
    op.execute(tsv_create_trigger)
    op.execute(tsv_create_index)

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'writing', sa.Column('extras', postgresql.JSON(), autoincrement=False, nullable=True))
    op.drop_column(u'writing', 'issue_id')
    op.add_column(u'review', sa.Column('book_reviewed', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(u'issue', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(u'issue', sa.Column('publish_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.create_unique_constraint(u'author_name_key', 'author', ['name'])
    # op.create_index('author_name_key', 'author', ['name'], unique=True)
    op.alter_column(u'author', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.add_column(u'author', sa.Column('profile_photo', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column(u'author', 'hidden')
    op.drop_column(u'author', 'bio')
    op.add_column(u'article', sa.Column('issue_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column(u'article', sa.Column('position', sa.INTEGER(), autoincrement=False))
    logger.warn('Article.position in v1 was originally not nullable, but this fails on downgrades.')
    op.create_table('post',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['id'], [u'writing.id'], name=u'post_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'post_pkey')
    )
    op.create_table('response',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('respondee_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id'], [u'writing.id'], name=u'response_id_fkey'),
    sa.ForeignKeyConstraint(['respondee_id'], [u'writing.id'], name=u'response_respondee_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'response_pkey')
    )
    op.drop_table('book')
    op.drop_table('writing_to_writing')
    op.drop_table('image_to_writing')
    op.drop_table('template')
    op.drop_table('image')
    op.drop_table('key_value')
    ### end Alembic commands ###

    # tsvector should be dropped in the auto-migration
    # so just drop the index and trigger
    op.execute('drop trigger if exists ts_update on writing;')
    op.execute('drop index if exists tsvector_idx;')
    op.drop_column(u'writing', 'tsvector')

    # Revert issue_id column
    op.execute(u'update article set issue_id = 1 where id in (1, 2, 3, 4);')
    logger.warn('Manually setting the issue_id for the first issues. This will fail if there are more issues past Dec. 2014.')