"""Make pictures a list

Revision ID: 06f78edd1f0a
Revises: 44717993e071
Create Date: 2024-05-10 14:45:31.488630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '06f78edd1f0a'
down_revision: Union[str, None] = '44717993e071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feedback_report', sa.Column('pictures', postgresql.ARRAY(sa.String()), nullable=True))
    op.create_unique_constraint(None, 'feedback_report', ['fr_id'])
    op.drop_column('feedback_report', 'picture')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feedback_report', sa.Column('picture', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'feedback_report', type_='unique')
    op.drop_column('feedback_report', 'pictures')
    # ### end Alembic commands ###
