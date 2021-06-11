"""v3 models

Revision ID: 5673f248d387
Revises: 345d55c22456
Create Date: 2016-03-17 20:05:01.115575

"""

# revision identifiers, used by Alembic.
revision = '5673f248d387'
down_revision = '345d55c22456'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import logging

logger = logging.getLogger(__name__)

def upgrade():
    op.drop_table('image_to_writing')
    op.drop_table('editors')
    op.drop_table('image')

    for table in ('author', 'article', 'review', 'book', 'tag'):
        op.rename_table(table, table + 's')

    for table in ('authors', 'books', 'tags'):
        op.add_column(table, sa.Column('mark_for_delete', sa.Boolean(), nullable=True))
        op.add_column(table, sa.Column('create_date', sa.DateTime(), server_default=sa.text(u'now()'), nullable=False))
        op.add_column(table, sa.Column('last_edited_date', sa.DateTime(), server_default=sa.text(u'now()'), nullable=True))
    op.add_column('writing', sa.Column('mark_for_delete', sa.Boolean(), nullable=True))


    # New tables
    op.create_table('intros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['writing.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('readings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['writing.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.drop_constraint(u'author_to_writing_author_id_fkey', 'author_to_writing', type_='foreignkey')
    op.create_foreign_key(u'author_to_writing_author_id_fkey', 'author_to_writing', 'authors', ['author_id'], ['id'])
    op.drop_constraint(u'tag_to_writing_tag_id_fkey', 'tag_to_writing', type_='foreignkey')
    op.create_foreign_key(u'tag_to_writing_tag_id_fkey', 'tag_to_writing', 'tags', ['tag_id'], ['id'])


def downgrade():
    op.drop_table('intros')
    op.drop_table('readings')

    for table in ('author', 'article', 'review', 'book', 'tag'):
        op.rename_table(table + 's', table)

    for table in ('author', 'writing', 'book', 'tag'):
        op.drop_column('mark_for_delete')
        op.drop_column('create_date')
        op.drop_column('last_edited_date')

    op.create_table('editors',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('username', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('password', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.Column('create_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column('last_edited_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column('email', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('password_updated', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column('author_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['author_id'], [u'author.id'], name=u'editors_author_id_fkey'),
        sa.PrimaryKeyConstraint('id', name=u'admin_pkey'),
        sa.UniqueConstraint('email', name=u'editors_email_key')
    )
    op.create_table('image_to_writing',
        sa.Column('image_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('writing_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['image_id'], [u'image.id'], name=u'image_to_writing_image_id_fkey'),
        sa.ForeignKeyConstraint(['writing_id'], [u'writing.id'], name=u'image_to_writing_writing_id_fkey')
    )
    op.create_table('image',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('filename', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('url', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('expired', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name=u'image_pkey')
    )

    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'tag_to_writing_tag_id_fkey', 'tag_to_writing', type_='foreignkey')
    op.create_foreign_key(u'tag_to_writing_tag_id_fkey', 'tag_to_writing', 'tag', ['tag_id'], ['id'])
    op.drop_constraint(u'author_to_writing_author_id_fkey', 'author_to_writing', type_='foreignkey')
    op.create_foreign_key(u'author_to_writing_author_id_fkey', 'author_to_writing', 'author', ['author_id'], ['id'])