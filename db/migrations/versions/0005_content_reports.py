"""Private queue of user-reported AI replies."""
from alembic import op
import sqlalchemy as sa
revision = '0005_content_reports'
down_revision = '0004_push_delivery'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('content_reports',
        sa.Column('message_id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reason', sa.String(32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_content_reports_user_id', 'content_reports', ['user_id'])

def downgrade():
    raise RuntimeError('Restore a verified backup instead of dropping reports')
