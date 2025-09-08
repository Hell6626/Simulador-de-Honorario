"""Add valor_mensalidade field to proposta table

Revision ID: add_valor_mensalidade_to_proposta
Revises: create_mensalidade_automatica_table
Create Date: 2024-12-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_valor_mensalidade_to_proposta'
down_revision = 'create_mensalidade_automatica_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add valor_mensalidade column to proposta table
    op.add_column('proposta', sa.Column('valor_mensalidade', sa.Numeric(precision=15, scale=2), nullable=True, default=0))
    
    # Update existing records to have valor_mensalidade = 0
    op.execute("UPDATE proposta SET valor_mensalidade = 0 WHERE valor_mensalidade IS NULL")


def downgrade():
    # Remove valor_mensalidade column from proposta table
    op.drop_column('proposta', 'valor_mensalidade')
