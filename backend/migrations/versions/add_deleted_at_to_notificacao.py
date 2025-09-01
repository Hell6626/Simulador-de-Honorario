"""Add deleted_at field to notificacao table

Revision ID: add_deleted_at_notificacao
Revises: c3d4e5f6g7h8_create_notificacao_table
Create Date: 2025-01-08 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_deleted_at_notificacao'
down_revision = 'c3d4e5f6g7h8_create_notificacao_table'
branch_labels = None
depends_on = None


def upgrade():
    """Add deleted_at column to notificacao table"""
    op.add_column('notificacao', 
        sa.Column('deleted_at', sa.DateTime(), nullable=True)
    )


def downgrade():
    """Remove deleted_at column from notificacao table"""
    op.drop_column('notificacao', 'deleted_at')
