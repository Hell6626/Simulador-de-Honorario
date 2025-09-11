"""Make CPF field optional in cliente table

Revision ID: 20250120_000
Revises: add_valor_mensalidade_to_proposta
Create Date: 2025-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250120_000'
down_revision = 'add_valor_mensalidade_to_proposta'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tornar o campo CPF não obrigatório na tabela cliente
    with op.batch_alter_table('cliente', schema=None) as batch_op:
        batch_op.alter_column('cpf',
               existing_type=sa.String(14),
               nullable=True)


def downgrade() -> None:
    # Reverter o campo CPF para obrigatório
    with op.batch_alter_table('cliente', schema=None) as batch_op:
        batch_op.alter_column('cpf',
               existing_type=sa.String(14),
               nullable=False)
