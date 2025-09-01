"""add percentual_desconto to proposta

Revision ID: a1b2c3d4e5f6
Revises: d40f383ff0d1
Create Date: 2025-01-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'd40f383ff0d1'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campo percentual_desconto na tabela proposta
    op.add_column('proposta', sa.Column('percentual_desconto', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    # Remover campo percentual_desconto da tabela proposta
    op.drop_column('proposta', 'percentual_desconto')
