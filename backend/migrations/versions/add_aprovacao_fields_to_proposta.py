"""Add aprovacao fields to proposta

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-01-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add aprovacao fields to proposta table
    op.add_column('proposta', sa.Column('requer_aprovacao', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('proposta', sa.Column('aprovada_por', sa.Integer(), nullable=True))
    op.add_column('proposta', sa.Column('data_aprovacao', sa.DateTime(), nullable=True))
    op.add_column('proposta', sa.Column('motivo_rejeicao', sa.Text(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key('fk_proposta_aprovada_por_funcionario', 'proposta', 'funcionario', ['aprovada_por'], ['id'])


def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('fk_proposta_aprovada_por_funcionario', 'proposta', type_='foreignkey')
    
    # Remove columns
    op.drop_column('proposta', 'motivo_rejeicao')
    op.drop_column('proposta', 'data_aprovacao')
    op.drop_column('proposta', 'aprovada_por')
    op.drop_column('proposta', 'requer_aprovacao')
