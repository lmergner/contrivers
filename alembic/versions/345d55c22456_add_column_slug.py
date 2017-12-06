"""add column slug

Revision ID: 345d55c22456
Revises: 17d02bbea2b2
Create Date: 2015-08-25 16:09:17.440641

"""

# revision identifiers, used by Alembic.
revision = '345d55c22456'
down_revision = '17d02bbea2b2'

from alembic import op
import sqlalchemy as sa

import logging

logger = logging.getLogger(__name__)

def upgrade():
    op.add_column('writing', sa.Column('slug', sa.String(250)))


def downgrade():
    op.drop_column('writing', 'slug')
