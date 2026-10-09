"""Bind push registrations to sessions and track provider receipts."""
from alembic import op
import sqlalchemy as sa
revision = '0004_push_delivery'
down_revision = '0003_credentials_deletion'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('push_tokens', sa.Column('session_id', sa.String(36), nullable=True))
    op.create_index('ix_push_tokens_session_id', 'push_tokens', ['session_id'])
    op.create_table('push_receipts',
        sa.Column('ticket_id', sa.String(100), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    raise RuntimeError('Restore a verified backup instead of dropping delivery state')
