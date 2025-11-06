"""add created_at, fix types, UTC

Revision ID: 4e8202bba562
Revises: 88bd0466d6f4
Create Date: 2025-11-06 19:53:08.343941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4e8202bba562'
down_revision: Union[str, Sequence[str], None] = '88bd0466d6f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем username как NULLable с временным значением
    op.add_column(
        'users',
        sa.Column('username', sa.String(), nullable=True)
    )
    # Заполняем username значениями из uuid (или другим логичным значением)
    op.execute("UPDATE users SET username = SUBSTRING(uuid, 1, 30) WHERE username IS NULL")
    # Теперь делаем NOT NULL
    op.alter_column('users', 'username', nullable=False)
    op.create_unique_constraint(None, 'users', ['username'])

    # Остальные изменения — без изменений
    op.add_column('users', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('medications', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('intake_history', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False))
    
    op.alter_column('intake_history', 'scheduled_time',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.TIMESTAMP(timezone=True),
                   existing_nullable=False)
    op.alter_column('intake_history', 'taken_time',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.TIMESTAMP(timezone=True),
                   existing_nullable=False)

    # Удаление invitation_codes — оставляем (пока не почините импорт)
    op.drop_index(op.f('ix_invitation_codes_code'), table_name='invitation_codes')
    op.drop_index(op.f('ix_invitation_codes_id'), table_name='invitation_codes')
    op.drop_table('invitation_codes')


def downgrade() -> None:
    # Сначала drop таблицы (чтобы FK не мешали)
    op.create_table('invitation_codes',
        sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('code', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('med_friend_id', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('expires_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('is_used', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['med_friend_id'], ['users.uuid'], name=op.f('invitation_codes_med_friend_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('invitation_codes_pkey'))
    )
    op.create_index(op.f('ix_invitation_codes_id'), 'invitation_codes', ['id'], unique=False)
    op.create_index(op.f('ix_invitation_codes_code'), 'invitation_codes', ['code'], unique=True)

    # Удаляем created_at
    op.drop_column('intake_history', 'created_at')
    op.drop_column('medications', 'created_at')
    op.drop_column('users', 'created_at')

    # Возвращаем timestamp без TZ
    op.alter_column('intake_history', 'taken_time',
                   existing_type=sa.TIMESTAMP(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   existing_nullable=False)
    op.alter_column('intake_history', 'scheduled_time',
                   existing_type=sa.TIMESTAMP(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   existing_nullable=False)

    # Возвращаем username в NULLable и удаляем
    op.alter_column('users', 'username', nullable=True)
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'username')
    # ### end Alembic commands ###
