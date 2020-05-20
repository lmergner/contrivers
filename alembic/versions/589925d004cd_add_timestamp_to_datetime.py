"""

add_timestamp_to_datetime

Revision ID: 589925d004cd
Revises: 203dfa6493b5
Create Date: 2015-07-16 14:23:29.674353

"""

# revision identifiers, used by Alembic.
revision = '589925d004cd'
down_revision = '203dfa6493b5'

from alembic import op
import sqlalchemy as sa

import logging

logger = logging.getLogger(__name__)

def upgrade():
    op.alter_column('writing', 'publish_date', type_ = sa.DateTime(timezone=True))
    op.alter_column('writing', 'last_edited_date', type_ = sa.DateTime(timezone=True))
    op.alter_column('writing', 'create_date', type_ = sa.DateTime(timezone=True))


def downgrade():
    op.alter_column('writing', 'publish_date', type_ = sa.DateTime(timezone=False))
    op.alter_column('writing', 'last_edited_date', type_ = sa.DateTime(timezone=False))
    op.alter_column('writing', 'create_date', type_ = sa.DateTime(timezone=False))

