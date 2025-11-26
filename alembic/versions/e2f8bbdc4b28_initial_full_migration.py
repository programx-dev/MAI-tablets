"""initial full migration

Revision ID: e2f8bbdc4b28
Revises: 
Create Date: 2025-11-26 00:13:17.157195

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e2f8bbdc4b28'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Users table
    op.create_table(
        'users',
        sa.Column('uuid', sa.String(), primary_key=True),
        sa.Column('username', sa.String(), nullable=False, unique=True),
        sa.Column('hash_password', sa.String(), nullable=False),
        sa.Column('relation_id', sa.String(), sa.ForeignKey('users.uuid'), nullable=True),
        sa.Column('last_synced_time', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    op.create_index(op.f('ix_users_uuid'), 'users', ['uuid'], unique=True)

    # Medications table
    op.create_table(
        'medications',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('patient_id', sa.String(), sa.ForeignKey('users.uuid'), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('form', sa.Text(), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('schedule_type', sa.Text(), nullable=False),
        sa.Column('week_days', sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column('interval_days', sa.Integer(), nullable=True),
        sa.Column('times_per_day', sa.ARRAY(sa.Time()), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("form IN ('tablet', 'drop', 'spray', 'other')", name='valid_form'),
        sa.CheckConstraint("schedule_type IN ('daily', 'weekly_days', 'every_x_days')", name='valid_schedule_type')
    )
    op.create_index(op.f('ix_medications_id'), 'medications', ['id'], unique=False)

    # Intake history table
    op.create_table(
        'intake_history',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('medication_id', sa.BigInteger(), sa.ForeignKey('medications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scheduled_time', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('taken_time', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("status IN ('taken', 'skipped')", name='valid_status')
    )
    op.create_index(op.f('ix_intake_history_id'), 'intake_history', ['id'], unique=False)

    # Invitation codes table
    op.create_table(
        'invitation_codes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('med_friend_id', sa.String(), sa.ForeignKey('users.uuid'), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    op.create_index(op.f('ix_invitation_codes_id'), 'invitation_codes', ['id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_invitation_codes_id'), table_name='invitation_codes')
    op.drop_table('invitation_codes')

    op.drop_index(op.f('ix_intake_history_id'), table_name='intake_history')
    op.drop_table('intake_history')

    op.drop_index(op.f('ix_medications_id'), table_name='medications')
    op.drop_table('medications')

    op.drop_index(op.f('ix_users_uuid'), table_name='users')
    op.drop_table('users')
