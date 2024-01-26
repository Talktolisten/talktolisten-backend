"""Add DOB to user table

Revision ID: 5c8d8c376c7b
Revises: 50393775784f
Create Date: 2024-01-25 13:53:17.250004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c8d8c376c7b'
down_revision: Union[str, None] = '50393775784f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('dob', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'dob')
    # ### end Alembic commands ###
