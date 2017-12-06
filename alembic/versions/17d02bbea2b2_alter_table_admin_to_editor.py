"""alter table admin to editor

Revision ID: 17d02bbea2b2
Revises: 5703f85b3a6a
Create Date: 2015-08-18 12:07:07.066993

"""

# revision identifiers, used by Alembic.
revision = '17d02bbea2b2'
down_revision = '5703f85b3a6a'

from alembic import op
import sqlalchemy as sa
import logging
import datetime

logger = logging.getLogger(__name__)

def upgrade():
    op.rename_table('admin', 'editors')


    with op.batch_alter_table('editors') as editors:
        editors.add_column(sa.Column('create_date', sa.DateTime(timezone=True)))
        editors.add_column(sa.Column('last_edited_date', sa.DateTime(timezone=True)))
        editors.add_column(sa.Column('email', sa.String(50), unique=True))
        editors.add_column(sa.Column('password_updated', sa.DateTime(timezone=True)))
        editors.add_column(sa.Column('author_id', sa.Integer(), sa.ForeignKey('author.id'), nullable=True))
        editors.alter_column('password', type_=sa.String(100), nullable=False)
        editors.alter_column('username', type_=sa.String(50), nullable=True)

    editor_tmp = sa.sql.table('editors', sa.sql.column('create_date'), sa.sql.column('last_edited_date'), sa.sql.column('email'), sa.sql.column('password_updated'), sa.sql.column('username'))
    op.execute(editor_tmp.update().values(
        create_date      =   datetime.datetime.utcnow(),
        last_edited_date =   datetime.datetime.utcnow(),
        password_updated =   datetime.datetime.utcnow()))
    op.execute(editor_tmp.update().where(editor_tmp.c.username=='lmergner').values(email='lmergner@gmail.com'))
    op.execute(editor_tmp.update().where(editor_tmp.c.username=='psinnott').values(email='psinnott@gmail.com'))
    op.alter_column('editors', 'create_date', nullable=False)
    op.alter_column('editors', 'last_edited_date', nullable=False)
    op.alter_column('editors', 'password_updated', nullable=False)
    op.alter_column('editors', 'email', nullable=False)


def downgrade():
    op.rename_table('editors', 'admin')
    with op.batch_alter_table('admin') as admin:
        admin.drop_column('email')
        admin.drop_column('create_date')
        admin.drop_column('last_edited_date')
        admin.drop_column('password_updated')
        admin.drop_column('author_id')
