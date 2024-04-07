"""make audio sample not nullable

Revision ID: e243a87758b8
Revises: 79605f3391f7
Create Date: 2024-04-07 15:01:12.209134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e243a87758b8'
down_revision: Union[str, None] = '79605f3391f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('voices', 'sample_url',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('voices', 'sample_url',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
