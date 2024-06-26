"""Add group chat

Revision ID: 8ddce7660b62
Revises: 14193890d9ad
Create Date: 2024-04-20 15:08:00.393547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ddce7660b62'
down_revision: Union[str, None] = '14193890d9ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group_chats',
    sa.Column('group_chat_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('group_chat_name', sa.String(), nullable=True),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('group_chat_profile_picture', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_message', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['last_message'], ['messages.message_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('group_chat_id'),
    sa.UniqueConstraint('group_chat_id')
    )
    op.create_table('group_chat_bots',
    sa.Column('group_chat_id', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=False),
    sa.Column('joined_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['bot_id'], ['bots.bot_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['group_chat_id'], ['group_chats.group_chat_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('group_chat_id', 'bot_id')
    )
    op.add_column('messages', sa.Column('group_chat_id', sa.Integer(), nullable=True))
    op.alter_column('messages', 'chat_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'messages', 'group_chats', ['group_chat_id'], ['group_chat_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.alter_column('messages', 'chat_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('messages', 'group_chat_id')
    op.drop_table('group_chat_bots')
    op.drop_table('group_chats')
    # ### end Alembic commands ###
